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

from .core import SpeechBuilder, ResponseBuilder, RequestHandler, validate_language


class URL(object):
    """
    :param str url: As str which points directly to a source which should be played by Clover
    """

    def __init__(self, url):
        self.value = url

    def __repr__(self):
        return "URL: {}".format(self.value)


class Message(object):
    """
    :param str message: Message of type str which Clova should speak out
    :param str language: Language code of the message. Can be ``ja``, ``ko`` or ``en``.
    """

    def __init__(self, message, language=None):
        self.text = message
        self.language = language

    def __repr__(self):
        return "Message: text:{}, language:{}".format(self.text, self.language)


class MessageSet(object):
    """
    :param brief: Can be of type :class:`str`, :class:`Message` or :class:`URL`
    :param verbose: Can be of type :class:`str`, :class:`Message` or :class:`URL`
        or a :class:`list` containing any of those three types
    """

    def __init__(self, brief, verbose):
        self.brief = brief
        self.verbose = verbose

    def __repr__(self):
        return "MessageSet: brief:{}, verbose:{}".format(self.brief, self.verbose)


class Clova(object):
    """Clova provides the easiest way to create your extension.

    :param str application_id: Set registered application id to verify all incoming requests
    :param str default_language: Set default language for all messages. Can be ``ja``, ``ko`` or ``en``.
    :param bool debug_mode: Use only for development. If set to True, request and applicationId verification are turned off
    :raises ValueError: if unsupported language is specified.
    :ivar RequestHandler handle: Helper to handle requests from CEK. Request handlers must be defined using the handler.

    Usage:
      Create :class:`Clova` instance:

      >>> from cek import Clova
      >>> clova = Clova(application_id='', default_language='jp', debug_mode=True)

      Define request handlers using (:attr:`Clova.handle`). Response can be created using :meth:`Clova.response`.

      >>> @clova.handle.launch
      ... def launch_request_handler(clova_request):
      ...     return clova.response("こんにちは世界。スキルを起動します")

      >>> @clova.handle.default
      ... def default_handler(clova_request):
      ...     return clova.response("もう一度お願いします")

      Plug into your web application using :meth:`Clova.route`:

      >>> rom flask import Flask, request, jsonify
      >>> app = Flask(__name__)
      >>> @app.route('/app', methods=['POST'])
      ... def my_service():
      ...     resp = clova.route(request.data, request.headers)
      ...     resp = jsonify(resp)
      ...     resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
      ...     return resp

    See docs for :meth:`Clova.route` and :meth:`Clova.response` for detailed usages.
    """

    def __init__(self, application_id, default_language="ja", debug_mode=False):

        self._speechBuilder = SpeechBuilder(default_language)
        self._responseBuilder = ResponseBuilder(default_language)
        self.handle = RequestHandler(application_id=application_id, debug_mode=debug_mode)

    def _response_value(self, message):
        """
        :param message: Can be of type :class:`str`, :class:`Message` or :class:`URL`
        :return: Dictionary with the format of a SpeechInfo with type 'plain_text' or with type 'url'
        """
        if isinstance(message, Message):
            return self._speechBuilder.plain_text(message=message.text, language=message.language)

        if isinstance(message, str):
            return self._speechBuilder.plain_text(message)

        if isinstance(message, URL):
            return self._speechBuilder.url(message.value)

        raise TypeError("Unsupported type found in Message:{}".format(message))

    def _response_values(self, messages):
        """
        :param list messages: :class:`list` containing objects of type :class:`str`, :class:`Message` or :class:`URL`
        :return: List of dictionaries with the format of a SpeechInfo with type 'plain_text' or with type 'url'
        """
        speech_values = []
        for messages in messages:
            value = self._response_value(messages)
            speech_values.append(value)

        return speech_values

    def _response_speech(self, message):
        """
        :param message: Can be of type :class:`str`, :class:`Message` or :class:`URL` or a :class:`list`,
            :class:`MessageSet` containing any of these types
        :return: Return simple_speech, speech_list
        """
        if isinstance(message, list):
            speech_values = self._response_values(message)
            speech = self._speechBuilder.speech_list(speech_values)
        elif isinstance(message, MessageSet):

            verbose = message.verbose
            brief_value = self._response_value(message.brief)

            if isinstance(verbose, list):
                verbose_values = self._response_values(verbose)
                verbose_speech = self._speechBuilder.speech_list(verbose_values)
            else:
                verbose_value = self._response_value(verbose)
                verbose_speech = self._speechBuilder.simple_speech(verbose_value)

            speech = self._speechBuilder.speech_set(brief=brief_value, verbose=verbose_speech)

        else:
            speech_value = self._response_value(message)
            speech = self._speechBuilder.simple_speech(speech_value)

        return speech

    def route(self, body, header):
        """Route request from CEK to handlers

        Depending on the request type (intent, launch, etc), the function routes
        the request to the proper handler defined by the user and returns the response
        as a dictionary. Request verification is done per request before routing.

        The method is an alias to :meth:`cek.core.RequestHandler.route_request`.

        :param bytes body: Binary Request body from CEK
        :param dict header: Request Header as a dictionary
        :return: Returns body for CEK response
        :rtype: cek.core.Response
        :raises cryptography.exceptions.InvalidSignature: (non-debug mode only) if request verification failed.
        :raises RuntimeError: (non-debug mode only) if application id is incorrect.

        Usage:
            >>> from cek import Clova
            >>> clova = Clova(application_id="", default_language="ja", debug_mode=True)
            >>> from flask import Flask, request, jsonify
            >>> app = Flask(__name__)
            >>> @app.route('/app', methods=['POST'])
            ... def my_service():
            ...     resp = clova.route(request.data, request.headers)
            ...     resp = jsonify(resp)
            ...     resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
            ...     return resp
        """
        return self.handle.route_request(request_body=body, request_header_dict=header)

    def response(self, message, reprompt=None, end_session=False):
        """Create a Response that should be sent back to CEK

        :param message: Can be of type :class:`str`, :class:`Message` or :class:`URL` or a :class:`list`,
            :class:`MessageSet` containing any of these types
        :param reprompt: Can be of type :class:`str`, :class:`Message` or :class:`URL` or a :class:`list`,
            :class:`MessageSet` containing any of these types
        :param bool end_session: Whether Clova should continue to listen or end the session
        :return: Response containing passed message
        :rtype: cek.core.Response
        :raises ValueError: if unsupported language is specified.

        Usage:
            >>> import cek
            >>> from cek import Clova
            >>> from pprint import pprint
            >>> clova = Clova(application_id="", default_language="ja", debug_mode=True)

            Simplest case:

            >>> resp = clova.response("こんにちは")
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

            With explicit language:

            >>> resp = clova.response(cek.Message("English", language="en"))
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SimpleSpeech',
                                           'values': {'lang': 'en',
                                                      'type': 'PlainText',
                                                      'value': 'English'}},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}

            URL:

            >>> resp = clova.response(cek.URL("https://dummy.mp3"))
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SimpleSpeech',
                                           'values': {'lang': '',
                                                      'type': 'URL',
                                                      'value': 'https://dummy.mp3'}},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}

            List:

            >>> resp = clova.response(["こんにちは", cek.URL("https://dummy.mp3")])
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

            With reprompt message:

            >>> resp = clova.response("こんにちは", reprompt="聞こえていますか？")
            >>> pprint(resp)
            {'response': {'card': {},
                          'directives': [],
                          'outputSpeech': {'type': 'SimpleSpeech',
                                           'values': {'lang': 'ja',
                                                      'type': 'PlainText',
                                                      'value': 'こんにちは'}},
                          'reprompt': {'outputSpeech': {'type': 'SimpleSpeech',
                                                        'values': {'lang': 'ja',
                                                                   'type': 'PlainText',
                                                                   'value': '聞こえていますか？'}}},
                          'shouldEndSession': False},
             'sessionAttributes': {},
             'version': '1.0'}
        """
        if isinstance(message, list):
            speech_values = self._response_values(message)
            response = self._responseBuilder.speech_list(speech_values=speech_values, end_session=end_session)
        elif isinstance(message, MessageSet):
            verbose = message.verbose
            brief_value = self._response_value(message.brief)

            if isinstance(verbose, list):
                verbose_values = self._response_values(verbose)
                verbose_speech = self._speechBuilder.speech_list(verbose_values)
            else:
                verbose_value = self._response_value(verbose)
                verbose_speech = self._speechBuilder.simple_speech(verbose_value)

            response = self._responseBuilder.speech_set(brief=brief_value, verbose=verbose_speech, end_session=end_session)

        else:
            value = self._response_value(message)
            response = self._responseBuilder.simple_speech(value, end_session=end_session)

        if reprompt is not None:
            speech = self._response_speech(reprompt)
            response = self._responseBuilder.add_reprompt(response=response, speech=speech)

        return response
