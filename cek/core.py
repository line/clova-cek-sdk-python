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

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# https://clova-developers.line.me/guide/#/CEK/References/CEK_API.md#CustomExtSpeechInfoObject
supported_languages = ['en', 'ja', 'ko']


class ApplicationIdMismatch(Exception):
    """ Application Id does not match """
    pass


def validate_language(lang):
    if lang not in supported_languages:
        raise ValueError('Lang: "{}" is not supported. Currently supported languages are en, ja and ko.'.format(lang))
    return lang


class User(object):
    """Type which holds details about user.

        :param dict user_dict: Dictionary represents the user field from the CEK request

        :ivar str id: Clova ID of the user.
        :ivar str access_token: Access token of the user.
    """
    def __init__(self, user_dict):
        self._user = user_dict

    @property
    def id(self):
        return self._user['userId']

    @property
    def access_token(self):
        return self._user['accessToken']


class Session(object):
    """Type which holds details about each users session.

        :param dict session_dict: Dictionary represents the session field from the CEK request

        :ivar str id: is the session id.
        :ivar bool is_new: distinguishes whether the request message is for a new session or the existing session.
        :ivar dict attributes: used in multi-turn dialogue and contains the information set in previous response.sessionAttributes.
        :ivar User user: Current user connected to the device. Can be different from context.user.
    """

    def __init__(self, session_dict):
        self._session = session_dict

    @property
    def id(self):
        return self._session['sessionId']

    @property
    def is_new(self):
        return self._session['new']

    @property
    def attributes(self):
        return self._session.setdefault('sessionAttributes', {})

    @property
    def user(self):
        return User(self._session['user'])


class Device(object):
    """Type which holds details about user.

        :param dict device_dict: Dictionary represents the device field from the CEK request

        :ivar str id: ID of the device.
    """

    def __init__(self, device_dict):
        self._device = device_dict

    @property
    def id(self):
        return self._device['deviceId']


class AudioPlayer(object):
    """Type which holds details of the media content currently being played or played last.

    :param dict audio_player_dict: Dictionary represents the AudioPlayer field from the CEK request

    :ivar num offset: is the most recent playback position of the recently played media in milliseconds.
    :ivar num total: is the total duration of the recently played media in milliseconds.
    :ivar str activity: is indicating the state of player. Can be "IDLE", "PLAYING", "PAUSED" or "STOPPED"
    :ivar dict stream: contains details of the currently playing media. TODO: AudioStreamInfoObject specs are still wip
    """

    def __init__(self, audio_player_dict):
        self._audio_player = audio_player_dict

    @property
    def offset(self):
        return self._audio_player.get('offsetInMilliseconds', 0)

    @property
    def total(self):
        return self._audio_player.get('totalInMilliseconds', 0)

    @property
    def activity(self):
        return self._audio_player['playerActivity']

    @property
    def stream(self):
        return self._audio_player.get('stream', None)


class Context(object):
    """Type which holds context information of the client.

    :param dict context_dict: Dictionary represents the context from a CEK request

    :ivar AudioPlayer audio_player: holds details of media content currently being played or played last. Can be None if empty.
    :ivar Device device: contains information of the client device.
    :ivar User user: default User of the device.
    """

    def __init__(self, context_dict):
        self._context = context_dict

    @property
    def audio_player(self):
        if 'AudioPlayer' in self._context:
            return AudioPlayer(self._context['AudioPlayer'])
        else:
            return None

    @property
    def device(self):
        return Device(self._context['device'])

    @property
    def user(self):
        return User(self._context['System']['user'])


class Request(object):
    """Type represents a request from CEK

    :param dict request_dict: Dictionary represents a request from CEK


    :ivar str type: type of request. Can be IntentRequest, EventRequest, LaunchRequest, SessionEndedRequest

    :ivar Context context: context of the current request from CEK.
    :ivar str application_id: application id.
    """

    def __init__(self, request_dict):
        self._request = request_dict['request']
        self._session = request_dict['session']
        self._context = request_dict['context']

        self.session = Session(request_dict['session'])
        self.version = request_dict['version']

    @classmethod
    def from_dict(cls, request_dict):
        """
        Factory method to create correct Response depending on request type

        :param dict request_dict: Dictionary represents a request from CEK
        """
        request_type = request_dict['request']['type']
        if request_type == 'IntentRequest':
            return IntentRequest(request_dict)
        elif request_type == 'EventRequest':
            return EventRequest(request_dict)
        elif request_type == 'LaunchRequest':
            return LaunchRequest(request_dict)
        elif request_type == 'SessionEndedRequest':
            return EndRequest(request_dict)
        else:
            raise ValueError("Request Type not supported.")

    @property
    def type(self):
        return self._request['type']

    @property
    def context(self):
        return Context(self._context)

    @property
    def application_id(self):
        return self._context['System']['application']['applicationId']

    def verify_application_id(self, application_id):
        """Verify application id

        :raises ApplicationIdMismatch: if application id is incorrect.
        """
        if self.application_id != application_id:
            raise ApplicationIdMismatch(
                "Request contains wrong ApplicationId:{}. This request was not meant to be sent to this Application.".format(application_id))


class LaunchRequest(Request):
    """Type represents a LaunchRequest from CEK"""
    pass


class EndRequest(Request):
    """Type represents an EndRequest from CEK"""
    pass


class IntentRequest(Request):
    """Type represents an IntentRequest from CEK

    :ivar str name: name of the intent
    :ivar dict slots_dict: slot values as dictionary.
    """

    @property
    def name(self):
        return self._request['intent']['name']

    @property
    def slots_dict(self):
        slots = self._request['intent']['slots']
        return {slot_name: slots[slot_name]['value'] for slot_name in slots}

    def slot_value(self, slot_name):
        """Returns slot value or None if missing.

        :param str slot_name: slot name
        :returns: slot value if exists, None otherwise.
        :rtype: str

        Usage:
          >>> intent.slot_value('Light')
          '電気'
        """
        slots = self._request['intent']['slots']
        if slots is not None and slot_name in slots:
            return slots[slot_name]['value']


class EventRequest(Request):
    """Type represents an EventRequest from CEK

    :ivar str id: is the dialog request id
    :ivar Event event: stores the information sent by the client to Clova.
    :ivar str timestamp: of when the client sends information to Clova (ISO 8601)
    """

    @property
    def id(self):
        return self._request['requestId']

    @property
    def event(self):
        return Event(self._request['event'])

    @property
    def timestamp(self):
        return self._request['timestamp']


class Event(object):
    """Type represents the stored information sent by the client to Clova.

    :ivar str name: is the name of the event message sent by the client to Clova
    :ivar str namespace: is the namespace of the event message.
    :ivar objc payload: is the payload or partial payload of the event message sent by the client to Clova.
    """

    def __init__(self, event_dict):
        self._event_dict = event_dict

    @property
    def name(self):
        return self._event_dict['name']

    @property
    def namespace(self):
        return self._event_dict['namespace']

    @property
    def payload(self):
        return self._event_dict['payload']


class Response(dict):
    """Type represents a response from CEK

    :ivar dict session_attributes: Session attributes in a dictionary format
    :ivar dict reprompt: reprompt value, can be SimpleSpeech, SpeechSet or SpeechList.
    """
    @property
    def session_attributes(self):
        return self.setdefault('sessionAttributes', {})

    @session_attributes.setter
    def session_attributes(self, value):
        self['sessionAttributes'] = value

    @property
    def reprompt(self):
        return self['response'].setdefault('reprompt', {})

    @reprompt.setter
    def reprompt(self, value):
        self['response']['shouldEndSession'] = False
        self['response']['reprompt'] = {'outputSpeech': value}


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
        self._launch_key = 'LaunchRequest'
        self._intent_key = 'IntentRequest'
        self._event_key = 'EventRequest'
        self._end_key = 'SessionEndedRequest'
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

        self._handlers = {self._intent_key: {}}

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
        self._handlers[self._launch_key] = func
        return func

    def event(self, func):
        """Event handler called on EventRequest.

        :param func: Function

        Usage:
            >>> @clova_handler.event
            ... def event_request_handler(clova_request):
            ...
        """
        self._handlers[self._event_key] = func
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
            self._handlers[self._intent_key][intent] = func
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
        self._handlers[self._end_key] = func
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

        request = Request.from_dict(request_dict)

        if not self._use_debug_mode:
            request.verify_application_id(self._application_id)

        is_intent_request = isinstance(request, IntentRequest)
        if is_intent_request:
            if request.name in self._handlers[self._intent_key]:
                handler_fn = self._handlers[self._intent_key][request.name]
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
