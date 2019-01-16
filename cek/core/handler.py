# coding: utf-8

# Copyright 2018 LINE Corporation
#
# LINE Corporation licenses this file to you under the Apache License,
# version 2.0 (the "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at:
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import division, print_function, absolute_import

import json
import base64

from .models import Request
from .models import IntentRequest
from .models import Response

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# https://clova-developers.line.me/guide/#/CEK/References/CEK_API.md#CustomExtSpeechInfoObject
supported_languages = ['en', 'ja', 'ko']


def validate_language(lang):
    if lang not in supported_languages:
        raise ValueError('Lang: "{}" is not supported. Currently supported languages are en, ja and ko.'.format(lang))
    return lang


class SpeechBuilder(object):
    """Helper class to build speech objects that can be part of CEK response.

    :param str default_language: Set default language for all messages. Can be ``ja``, ``ko`` or ``en``.
    :raises ValueError: if unsupported language is specified.

    Usage:
        All the examples below assume the following helper is defined in advance.

        >>> from cek import SpeechBuilder
        >>> from pprint import pprint
        >>> speech_builder = SpeechBuilder(default_language="ja")

        Building a plain text object:

        >>> speech_builder.plain_text("こんにちは")
        {'type': 'PlainText', 'lang': 'ja', 'value': 'こんにちは'}
    """

    def __init__(self, default_language="ja"):
        self.default_language = validate_language(default_language)

    def _speech_info(self, type, value, language):
        """Build a speech info object

        :param str type: Can be 'URL' or 'PlainText'
        :param str value: Can be an URL or a message as a String
        :param str language: Language code of the message other wise empty
        :return: Dictionary in the format of a SpeechInfo
        :rtype: dict
        """
        return {
            'type': type,
            'lang': language,
            'value': value
        }

    def plain_text(self, message, language=None):
        """Build a PlainText object

        :param str message: String Message which clova should speak out
        :param str language: Language code of the message
        :return: Dictionary with the format of a SpeechInfo with type PlainText
        :rtype: dict
        :raises ValueError: if unsupported language is specified.

        Usage:
            >>> speech_builder.plain_text("こんにちは")
            {'type': 'PlainText', 'lang': 'ja', 'value': 'こんにちは'}
        """
        if language is None:
            language = self.default_language
        language = validate_language(language)
        return self._speech_info(type='PlainText', value=message, language=language)

    def url(self, url):
        """Build an URL object

        :param str url: URL of the audio file which should be played by clova
        :return: Dictionary with the format of a SpeechInfo with type URL
        :rtype: dict

        Usage:
            >>> speech_builder.url("https://dummy.mp3")
            {'type': 'URL', 'lang': '', 'value': 'https://dummy.mp3'}
        """
        return self._speech_info(type='URL', value=url, language='')

    def simple_speech(self, speech_value):
        """Build a SimpleSpeech object

        :param dict speech_value: speech_value can be plain_text or url SpeechInfo
        :return: Dictionary in the format of a SimpleSpeech
        :rtype: dict

        Usage:
            >>> text = builder.plain_text("こんにちは")
            >>> pprint(speech_builder.simple_speech(text))
            {'type': 'SimpleSpeech',
             'values': {'lang': 'ja', 'type': 'PlainText', 'value': 'こんにちは'}}
        """
        return {
            'type': 'SimpleSpeech',
            'values': speech_value
        }

    def speech_list(self, speech_values):
        """Build a SpeechList object

        :param list speech_values: List which can consist of plain_text SpeechInfo or url SpeechInfo
        :return: Dictionary in the format of a SpeechList
        :rtype: dict

        Usage:
            >>> from pprint import pprint
            >>> text = speech_builder.plain_text("こんにちは")
            >>> url = speech_builder.url("https://dummy.mp3")
            >>> speech_list = speech_builder.speech_list([text, url])
            >>> pprint(speech_list)
            {'type': 'SpeechList',
             'values': [{'lang': 'ja', 'type': 'PlainText', 'value': 'こんにちは'},
                        {'lang': '', 'type': 'URL', 'value': 'https://dummy.mp3'}]}
        """
        return {
            'type': 'SpeechList',
            'values': speech_values
        }

    def speech_set(self, brief, verbose):
        """Build a SpeechSet object

        :param dict brief: A Dictionary of a plain_text SpeechInfo or url SpeechInfo
        :param dict verbose: A Dictionary of a SpeechList or SimpleSpeech
        :return: Dictionary in the format of a SpeechSet
        :rtype: dict
        """
        return {
            'type': 'SpeechSet',
            'brief': brief,
            'verbose': verbose
        }


class ResponseBuilder(object):
    """Helper class to build responses for CEK

    :param str default_language: Set default language for all messages. Can be ``ja``, ``ko`` or ``en``.
    :raises ValueError: if unsupported language is specified.

    Usage:
        All the examples below assume the following helper is defined in advance.

        >>> from cek import SpeechBuilder, ResponseBuilder
        >>> from pprint import pprint
        >>> speech_builder = SpeechBuilder(default_language="ja")
        >>> response_builder = ResponseBuilder(default_language="ja")

        Building a SimpleSpeech response:

        >>> resp = response_builder.simple_speech_text("こんにちは")
        >>> pprint(resp)
        {'response': {'card': {},
                      'directives': [],
                      'outputSpeech': {'type': 'SimpleSpeech',
                                       'values': {'lang': 'ja',
                                                  'type': 'PlainText',
                                                  'value': 'こんにちは'}},
                      'shouldEndSession': False},
         'sessionAttributes': {},
         'version': '1.0'}
    """

    def __init__(self, default_language="ja"):
        self.default_language = validate_language(default_language)
        self.speechBuilder = SpeechBuilder(default_language=default_language)

    def _template(self):
        return {
            "version": "1.0",
            "sessionAttributes": {},
            "response": {
                "outputSpeech": {},
                "card": {},
                "directives": [],
                "shouldEndSession": True
            }
        }

    def simple_speech_text(self, message, language=None, end_session=False):
        """ Build SimpleSpeech response with plain_text value

        :param str message: String Request which clova should speak out
        :param str language: Language code of the message
        :param bool end_session: Whether Clova should continue to listen or end the session
        :return: Response that wraps a Dictionary in the format of a response for a SimpleSpeech
        :rtype: cek.core.Response
        :raises ValueError: if unsupported language is specified.

        Usage:
            >>> resp = response_builder.simple_speech_text("こんにちは")
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SimpleSpeech',
                                           'values': {'lang': 'ja',
                                                      'type': 'PlainText',
                                                      'value': 'こんにちは'}},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}
        """
        if language is None:
            language = self.default_language

        language = validate_language(language)
        speech_value = self.speechBuilder.plain_text(message=message, language=language)
        response = self.simple_speech(speech_value=speech_value, end_session=end_session)
        return response

    def simple_speech(self, speech_value, end_session=False):
        """Build a SimpleSpeech response

        :param dict speech_value: Value which can consist of plain_text SpeechInfo or url SpeechInfo
        :param bool end_session: Whether Clova should continue to listen or end the session
        :return: Response that wraps a Dictionary in the format of a response for a SimpleSpeech
        :rtype: cek.core.Response

        Usage:
            >>> text = speech_builder.plain_text("こんにちは")
            >>> resp = response_builder.simple_speech(text)
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SimpleSpeech',
                                           'values': {'lang': 'ja',
                                                      'type': 'PlainText',
                                                      'value': 'こんにちは'}},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}
        """
        response = self._template()
        response['response']['outputSpeech'] = self.speechBuilder.simple_speech(speech_value=speech_value)
        response['response']['shouldEndSession'] = end_session
        return Response(response)

    def speech_list(self, speech_values, end_session=False):
        """Build a SpeechList response

        :param list speech_values: List which can consist of plain_text SpeechInfo or url SpeechInfo
        :param bool end_session: Whether Clova should continue to listen or end the session
        :return: Response that wraps a Dictionary in the format of a response for a SpeechList
        :rtype: cek.core.Response

        Usage:
            >>> text = speech_builder.plain_text("こんにちは")
            >>> url = speech_builder.url("https://dummy.mp3")
            >>> resp = response_builder.speech_list([text, url])
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SpeechList',
                                           'values': [{'lang': 'ja',
                                                       'type': 'PlainText',
                                                       'value': 'こんにちは'},
                                                      {'lang': '',
                                                       'type': 'URL',
                                                       'value': 'https://dummy.mp3'}]},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}
        """
        response = self._template()
        response['response']['outputSpeech'] = self.speechBuilder.speech_list(speech_values)
        response['response']['shouldEndSession'] = end_session
        return Response(response)

    def speech_url(self, message, url, language=None, end_session=False):
        """Build a SpeechList response with a message and an URL

        :param str message: String Message which clova should speak out
        :param str url: String URL of the audio file which should be played by clova
        :param str language: Language code of the message
        :param bool end_session: Whether Clova should continue to listen or end the session
        :return: Response that wraps a Dictionary in the format of a response for a SpeechList
        :rtype: cek.core.Response
        :raises ValueError: if unsupported language is specified.

        Usage:
            >>> resp = response_builder.speech_url("音楽を再生します", "https://dummy.mp3")
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SpeechList',
                                           'values': [{'lang': 'ja',
                                                       'type': 'PlainText',
                                                       'value': '音楽を再生します'},
                                                      {'lang': '',
                                                       'type': 'URL',
                                                       'value': 'https://dummy.mp3'}]},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}
        """
        if language is None:
            language = self.default_language
        language = validate_language(language)
        plain_text_value = self.speechBuilder.plain_text(message=message, language=language)
        url_object = self.speechBuilder.url(url=url)
        speech_values = [plain_text_value, url_object]
        response = self.speech_list(speech_values=speech_values, end_session=end_session)
        return Response(response)

    def speech_set(self, brief, verbose, end_session=False):
        """Build a SpeechSet response

        :param dict brief: A Dictionary of a plain_text SpeechInfo or url SpeechInfo
        :param dict verbose: A Dictionary of a SpeechList or SimpleSpeech
        :param bool end_session: Whether Clova should continue to listen or end the session
        :return: Response that wraps a Dictionary in the format of a response for a SpeechSet
        :rtype: cek.core.Response
        """
        response = self._template()
        response['response']['outputSpeech'] = self.speechBuilder.speech_set(brief=brief, verbose=verbose)
        response['response']['shouldEndSession'] = end_session
        return Response(response)

    def add_reprompt(self, response, speech):
        """Add a repromt to your response. It is recommended to use a SimpleSpeech to keep the reprompt short

        :param dict-like response: Response Dictionary to which the reprompt should be added
        :param dict speech: Speech can be a Dictionary of Simple Speech, SpeechList or SpeechSet
        :return: Response with added Speech reprompt
        :rtype: dict-like
        """
        output_speech = {'outputSpeech': speech}
        response['response']['shouldEndSession'] = False
        response['response']['reprompt'] = output_speech

        return response


class RequestHandler(object):
    """Helper class to handle requests from CEK.

    :param str application_id: Application ID that was used to register this Extension f.e.
    :param bool debug_mode: When set to True, application_id and request verification are ignored.

    Usage:
      All the examples below assume the following helpers are defined in advance.

      >>> from cek import RequestHandler, ResponseBuilder
      >>> clova_handler = RequestHandler(application_id="", debug_mode=True)
      >>> builder = ResponseBuilder(default_language="ja", debug_mode=False)

      Defining handlers can be done by decorators:

      >>> @clova_handler.launch
      ... def launch_request_handler(clova_request):
      ...     return builder.simple_speech_text("こんにちは世界。スキルを起動します")

      >>> @clova_handler.default
      ... def default_handler(clova_request):
      ...     return builder.simple_speech_text("もう一度お願いします")

      If you have defined request handlers, then setup a web API endpoint as follows:

      >>> rom flask import Flask, request, jsonify
      >>> app = Flask(__name__)
      >>> @app.route('/app', methods=['POST'])
      ... def my_service():
      ...     resp = clova_handler.route_request(request.data, request.headers)
      ...     resp = jsonify(resp)
      ...     resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
      ...     return resp
    """

    def __init__(self, application_id, debug_mode=False):
        self._default_key = '_default_'
        self._use_debug_mode = debug_mode
        self._application_id = application_id

        __cek_public_key_data = b"""
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwiMvQNKD/WQcX9KiWNMb
nSR+dJYTWL6TmqqwWFia69TyiobVIfGfxFSefxYyMTcFznoGCpg8aOCAkMxUH58N
0/UtWWvfq0U5FQN9McE3zP+rVL3Qul9fbC2mxvazxpv5KT7HEp780Yew777cVPUv
3+I73z2t0EHnkwMesmpUA/2Rp8fW8vZE4jfiTRm5vSVmW9F37GC5TEhPwaiIkIin
KCrH0rXbfe3jNWR7qKOvVDytcWgRHJqRUuWhwJuAnuuqLvqTyAawqEslhKZ5t+1Z
0GN8b2zMENSuixa1M9K0ZKUw3unzHpvgBlYmXRGPTSuq/EaGYWyckYz8CBq5Lz2Q
UwIDAQAB
-----END PUBLIC KEY-----
"""
        self._public_key = load_pem_public_key(__cek_public_key_data, backend=default_backend())

        self._handlers = {Request.intent_key: {}}

    def default(self, func):
        """Default handler

        :param func: Function

        Usage:
            >>> @clova_handler.default
            ... def default_handler(clova_request):
            ...     return builder.simple_speech_text("もう一度お願いします")
        """
        self._handlers[self._default_key] = func
        return func

    def launch(self, func):
        """Launch handler called on LaunchRequest.

        :param func: Function

        Usage:
            >>> @clova_handler.launch
            ... def launch_request_handler(clova_request):
            ...     return builder.simple_speech_text("こんにちは世界。スキルを起動します")
        """
        self._handlers[Request.launch_key] = func
        return func

    def event(self, func):
        """Event handler called on EventRequest.

        :param func: Function

        Usage:
            >>> @clova_handler.event
            ... def event_request_handler(clova_request):
            ...
        """
        self._handlers[Request.event_key] = func
        return func

    def intent(self, intent):
        """Intent handler called on IntentRequest.

        :param str intent: intent name

        Usage:
            >>> @clova_handler.intent("Clova.YesIntent")
            ... def intent_handler(clova_request):
            ...     return builder.simple_speech_text("はい、わかりました。")
        """
        def _handler(func):
            self._handlers[Request.intent_key][intent] = func
            return func
        return _handler

    def end(self, func):
        """End handler called on SessionEndedRequest.

        :param func: Function

        Usage:
            >>> @clova_handler.end
            ... def end_handler(clova_request):
            ...     # Session ended, this handler can be used to clean up
            ...     return
        """
        self._handlers[Request.session_ended_key] = func
        return func

    def route_request(self, request_body, request_header_dict):
        """Route request from CEK.

        :param bytes request_body: Binary Request body from CEK
        :param dict request_header_dict: Request Header as dictionary
        :return: Returns body for CEK response
        :rtype: cek.core.Response
        :raises cryptography.exceptions.InvalidSignature: (non-debug mode only) if request verification failed.
        :raises cek.ApplicationIdMismatch: (non-debug mode only) if application id is incorrect.

        Usage:
            >>> from flask import Flask, request, Response
            >>> app = Flask(__name__)
            >>> @app.route('/app', methods=['POST'])
            ... def my_service():
            ...     resp = clova_handler.route_request(request.data, request.headers)
            ...     resp = jsonify(resp)
            ...     resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
            ...     return resp
        """
        if not self._use_debug_mode:
            self._verify_request(request_body=request_body,
                                 request_header_dict=request_header_dict)

        body_string = request_body.decode("utf-8")
        request_dict = json.loads(body_string)

        handler_fn = self._handlers[self._default_key]

        request = Request.create(request_dict)

        if not self._use_debug_mode:
            request.verify_application_id(self._application_id)

        is_intent_request = isinstance(request, IntentRequest)
        if is_intent_request:
            if request.name in self._handlers[Request.intent_key]:
                handler_fn = self._handlers[Request.intent_key][request.name]
        elif request.type in self._handlers:
            handler_fn = self._handlers[request.type]

        return handler_fn(request)

    def _verify_request(self, request_body, request_header_dict):
        """
        :param request_body: binary body of request that needs to be verified
        :param request_header_dict: request header as a dictionary
        :return: True if verification of the request body was successful otherwise false
        """
        request_header_lowercase = {key.lower(): value for key, value in request_header_dict.items()}
        signature_base64 = request_header_lowercase['signaturecek']
        signature = base64.b64decode(signature_base64)

        self._public_key.verify(signature,
                                request_body,
                                padding.PKCS1v15(),
                                hashes.SHA256())
