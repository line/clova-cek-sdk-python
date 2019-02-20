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


class ApplicationIdMismatch(Exception):
    """ Application Id does not match. """
    pass


class User(object):
    """Type which holds details about user.

        :param dict user_dict: Dictionary represents the user field from the CEK request.

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
    """Type which holds details about each user's session.

        :param dict session_dict: Dictionary represents the session field from the CEK request.

        :ivar str id: is the session id.
        :ivar bool is_new: distinguishes whether the request message is for a new session or the existing session.
        :ivar dict attributes: used in multi-turn dialogue and contains the information set in previous response.sessionAttributes.
        :ivar User user: Current user connected to the device. Can be different from context.user.
    """

    def __init__(self, session_dict):
        self._session = session_dict
        self._user = User(session_dict['user'])

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
        return self._user


class Device(object):
    """Type which holds details about user's device.

        :param dict device_dict: Dictionary represents the device field from the CEK request.

        :ivar str id: ID of the device.
    """

    def __init__(self, device_dict):
        self._device = device_dict

    @property
    def id(self):
        return self._device['deviceId']


class AudioPlayer(object):
    """Type which holds details of the media content currently being played or played last.

    :param dict audio_player_dict: Dictionary represents the AudioPlayer field from the CEK request.

    :ivar num offset: is the most recent playback position of the recently played media in milliseconds.
    :ivar num total: is the total duration of the recently played media in milliseconds.
    :ivar str activity: is indicating the state of player. Can be "IDLE", "PLAYING", "PAUSED" or "STOPPED".
    :ivar dict stream: contains details of the currently playing media. TODO: AudioStreamInfoObject specs are still WIP.
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

    :param dict context_dict: Dictionary represents the context from a CEK request.

    :ivar AudioPlayer audio_player: holds details of media content currently being played or played last. Can be None if empty.
    :ivar Device device: contains information of the client device.
    :ivar User user: default User of the device.
    """

    def __init__(self, context_dict):
        self._context = context_dict
        self._user = User(context_dict['System']['user'])
        self._device = Device(context_dict['device'])
        if 'AudioPlayer' in context_dict:
            self._audioPlayer = AudioPlayer(context_dict['AudioPlayer'])
        else:
            self._audioPlayer = None

    @property
    def audio_player(self):
        return self._audioPlayer

    @property
    def device(self):
        return self._device

    @property
    def user(self):
        return self._user


class Request(object):
    """Type represents a request from CEK.

    :param dict request_dict: Dictionary represents a request from CEK.

    :cvar str launch_key: Key to identify the 'LaunchRequest' request type.
    :cvar str intent_key: Key to identify the 'IntentRequest' request type.
    :cvar str event_key: Key to identify the 'EventRequest' request type.
    :cvar str session_ended_key: Key to identify the 'SessionEndedRequest' request type.

    :ivar str type: type of request. Can be IntentRequest, EventRequest, LaunchRequest, SessionEndedRequest.
    :ivar Context context: context of the current request from CEK.
    :ivar str application_id: application id.
    """

    launch_key = 'LaunchRequest'
    intent_key = 'IntentRequest'
    event_key = 'EventRequest'
    session_ended_key = 'SessionEndedRequest'

    def __init__(self, request_dict):
        self._request = request_dict['request']
        self._session = request_dict['session']
        self._context = request_dict['context']

        self.session = Session(request_dict['session'])
        self.version = request_dict['version']

    @classmethod
    def create(cls, request_dict):
        """
        Factory method to create correct Response depending on request type.

        :param dict request_dict: Dictionary represents a request from CEK.
        """
        request_type = request_dict['request']['type']
        if request_type == cls.intent_key:
            return IntentRequest(request_dict)
        elif request_type == cls.event_key:
            return EventRequest(request_dict)
        elif request_type == cls.launch_key:
            return LaunchRequest(request_dict)
        elif request_type == cls.session_ended_key:
            return SessionEndedRequest(request_dict)
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
    """Type represents a LaunchRequest from CEK."""
    pass


class SessionEndedRequest(Request):
    """Type represents an SessionEndedRequest from CEK."""
    pass


class IntentRequest(Request):
    """Type represents an IntentRequest from CEK.

    :ivar str name: name of the intent.
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
        >>> @clova.handle.intent("TurnOn")
        >>> def turn_on_handler(request):
        >>>     request.slot_value('Light')
          '電気'
        """
        slots = self._request['intent']['slots']
        if slots is not None and slot_name in slots:
            return slots[slot_name]['value']


class EventRequest(Request):
    """Type represents an EventRequest from CEK.

    :ivar str id: is the dialog request id.
    :ivar Event event: stores the information sent by the client to Clova.
    :ivar str timestamp: of when the client sends information to Clova (ISO 8601).
    """

    def __init__(self, request_dict):
        super(EventRequest, self).__init__(request_dict)
        self._event = Event(self._request['event'])

    @property
    def id(self):
        return self._request['requestId']

    @property
    def event(self):
        return self._event

    @property
    def timestamp(self):
        return self._request['timestamp']


class Event(object):
    """Type represents the stored information sent by the client to Clova.

    :ivar str name: is the name of the event message sent by the client to Clova.
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
    """Type represents a response from CEK.

    :ivar dict session_attributes: Session attributes in a dictionary format.
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
