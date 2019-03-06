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

import unittest
from cek import Clova
import cek

from data.requests import LAUNCH_REQUEST_BODY, INTENT_REQUEST_BODY, END_REQUEST_BODY, EVENT_REQUEST_BODY, AUDIOPLAYER_EVENT_REQUEST_BODY, DEFAULT_REQUEST_BODY, GUIDE_REQUEST_BODY, NO_REQUEST_BODY


clova = Clova(application_id="com.line.myApplication", default_language="en", debug_mode=True)

mocked_header = {"": ""}


@clova.handle.launch
def launch_request_handler(launch_request):
    return clova.response("Hello! Welcome to my Service!")


@clova.handle.intent("TurnOn")
def turn_on_handler(intent_request):
    return clova.response(message="Turned on Something!", reprompt="Reprompt Message.")


@clova.handle.intent("TurnOff")
def turn_off_handler(intent_request):
    return clova.response(message="Turned off Something", end_session=True)


@clova.handle.event
def event_request_handler(event_request):
    event = event_request.event

    if event.namespace == 'ClovaSkill':
        if event.name == 'SkillEnabled':
            pass
        if event.name == 'SkillDisabled':
            pass
    elif event.namespace == 'AudioPlayer':
        if event.name == 'PlayStopped':
            player = event_request.context.audio_player
            assert player.activity == 'STOPPED', "Invalid request state for event PlayStopped."
    else:
        assert False, "Doesn't handle all events."


@clova.handle.end
def intent_handler(clova_request):
    return clova.response("Bye Bye!")


# Handles Build in Intents
@clova.handle.intent("Clova.GuideIntent")
def guide_intent(intent_request):
    attributes = intent_request.session.attributes
    # The session_attributes in the current response will become session_attributes in the next request
    message = "I can switch things off and on!"
    if 'HasExplainedService' in attributes:
        message = "I just explained you what i can do!"

    response = clova.response(message)
    response.session_attributes = {'HasExplainedService': True}

    return response


@clova.handle.intent("Clova.CancelIntent")
def cancel_intent(intent_request):
    return clova.response(message="Action canceled!", end_session=True)


@clova.handle.intent("Clova.YesIntent")
def yes_intent(intent_request):
    return clova.response("Yes, that's good!")


@clova.handle.intent("Clova.NoIntent")
def no_intent(intent_request):
    cek_message = cek.Message(message="はい、わかりました！", language="ja")
    return clova.response(cek_message)


# In case no intent could be matched
@clova.handle.default
def default_handler(clova_request):
    return clova.response("Sorry, I don't understand!")


class Test_CEKBase(unittest.TestCase):

    def test_launch_handler(self):
        response_dict = clova.route(body=LAUNCH_REQUEST_BODY, header=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['type'], 'PlainText')
        self.assertEqual(output_speech['values']['lang'], 'en')
        self.assertEqual(output_speech['values']['value'], 'Hello! Welcome to my Service!')

    def test_intent_handler(self):
        response_dict = clova.route(body=INTENT_REQUEST_BODY, header=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Turned on Something!')

    def test_intent_with_reprompt(self):
        response_dict = clova.route(body=INTENT_REQUEST_BODY, header=mocked_header)
        output_speech = response_dict['response']['reprompt']['outputSpeech']
        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['type'], 'PlainText')
        self.assertEqual(output_speech['values']['lang'], 'en')
        self.assertEqual(output_speech['values']['value'], 'Reprompt Message.')

    def test_event_handler(self):
        response = clova.route(body=EVENT_REQUEST_BODY, header=mocked_header)

        self.assertIsNone(response)

    def test_event_handler_audio_player(self):
        response = clova.route(body=AUDIOPLAYER_EVENT_REQUEST_BODY, header=mocked_header)

        self.assertIsNone(response)

    def test_end_handler(self):
        response_dict = clova.route(body=END_REQUEST_BODY, header=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Bye Bye!')

    def test_no_handler(self):
        response_dict = clova.route(body=NO_REQUEST_BODY, header=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'はい、わかりました！')

    def test_guide_handler(self):
        response_dict = clova.route(body=GUIDE_REQUEST_BODY, header=mocked_header)
        output_speech = response_dict['response']['outputSpeech']
        has_explained_service = response_dict['sessionAttributes']['HasExplainedService']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertTrue(has_explained_service)
        self.assertEqual(output_speech['values']['value'], 'I can switch things off and on!')

    def test_response_message(self):
        message = cek.Message("Hello! How are you?")
        response = clova.response(message)
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['lang'], 'en')
        self.assertEqual(output_speech['values']['type'], 'PlainText')
        self.assertEqual(output_speech['values']['value'], 'Hello! How are you?')

    def test_response_message_language(self):
        message = cek.Message(message="こんにちは！", language='ja')
        response = clova.response(message)
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['lang'], 'ja')
        self.assertEqual(output_speech['values']['type'], 'PlainText')
        self.assertEqual(output_speech['values']['value'], 'こんにちは！')

    def test_response_text(self):
        response = clova.response("Hello! How are you?")
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['lang'], 'en')
        self.assertEqual(output_speech['values']['type'], 'PlainText')
        self.assertEqual(output_speech['values']['value'], 'Hello! How are you?')

    def test_response_url(self):
        url = cek.URL(url='http://my.soundfile.mp3')
        response = clova.response(url)
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['lang'], '')
        self.assertEqual(output_speech['values']['type'], 'URL')
        self.assertEqual(output_speech['values']['value'], 'http://my.soundfile.mp3')

    def test_response_list(self):
        url = cek.URL('http://my.soundfile.mp3')
        message1 = cek.Message("Hello! How are you?")
        message2 = "Bye bye!"

        response = clova.response([message1, url, message2])
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SpeechList')
        self.assertEqual(output_speech['values'][0]['lang'], 'en')
        self.assertEqual(output_speech['values'][0]['type'], 'PlainText')
        self.assertEqual(output_speech['values'][0]['value'], 'Hello! How are you?')

        self.assertEqual(output_speech['values'][1]['lang'], '')
        self.assertEqual(output_speech['values'][1]['type'], 'URL')
        self.assertEqual(output_speech['values'][1]['value'], 'http://my.soundfile.mp3')

        self.assertEqual(output_speech['values'][2]['lang'], 'en')
        self.assertEqual(output_speech['values'][2]['type'], 'PlainText')
        self.assertEqual(output_speech['values'][2]['value'], 'Bye bye!')

    def test_response_message_set_verbose_list(self):
        message_set = cek.MessageSet(brief="title", verbose=["First Message", cek.Message("Second Message", "en")])
        response = clova.response(message_set)
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SpeechSet')
        self.assertEqual(output_speech['brief']['lang'], 'en')
        self.assertEqual(output_speech['brief']['type'], 'PlainText')
        self.assertEqual(output_speech['brief']['value'], 'title')

        self.assertEqual(output_speech['verbose']['type'], 'SpeechList')

        self.assertEqual(output_speech['verbose']['values'][0]['lang'], 'en')
        self.assertEqual(output_speech['verbose']['values'][0]['type'], 'PlainText')
        self.assertEqual(output_speech['verbose']['values'][0]['value'], 'First Message')

        self.assertEqual(output_speech['verbose']['values'][1]['lang'], 'en')
        self.assertEqual(output_speech['verbose']['values'][1]['type'], 'PlainText')
        self.assertEqual(output_speech['verbose']['values'][1]['value'], 'Second Message')

    def test_response_message_set_verbose_simple(self):
        message_set = cek.MessageSet(brief="title", verbose="Simple detailed Message")
        response = clova.response(message_set)
        output_speech = response['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SpeechSet')
        self.assertEqual(output_speech['brief']['lang'], 'en')
        self.assertEqual(output_speech['brief']['type'], 'PlainText')
        self.assertEqual(output_speech['brief']['value'], 'title')

        self.assertEqual(output_speech['verbose']['type'], 'SimpleSpeech')

        self.assertEqual(output_speech['verbose']['values']['lang'], 'en')
        self.assertEqual(output_speech['verbose']['values']['type'], 'PlainText')
        self.assertEqual(output_speech['verbose']['values']['value'], 'Simple detailed Message')

    def test_error_nested_message_set(self):
        message_set = cek.MessageSet(brief="title", verbose=["One Message", cek.Message("Other Message", "en")])
        nested_message_set = cek.MessageSet(brief="title", verbose=message_set)

        with self.assertRaises(TypeError):
            clova.response(nested_message_set)

    def test_reprompt(self):
        response = clova.response(message="How can I help you?", reprompt="Are you still there?")

        response_output_speech = response['response']['outputSpeech']
        reprompt_output_speech = response['response']['reprompt']['outputSpeech']

        self.assertEqual(response_output_speech['type'], 'SimpleSpeech')
        self.assertEqual(response_output_speech['values']['lang'], 'en')
        self.assertEqual(response_output_speech['values']['type'], 'PlainText')
        self.assertEqual(response_output_speech['values']['value'], 'How can I help you?')

        self.assertEqual(reprompt_output_speech['type'], 'SimpleSpeech')
        self.assertEqual(reprompt_output_speech['values']['lang'], 'en')
        self.assertEqual(reprompt_output_speech['values']['type'], 'PlainText')
        self.assertEqual(reprompt_output_speech['values']['value'], 'Are you still there?')

    def test_wrong_language(self):
        # Test builders
        for lang in ["es", "jp"]:
            with self.assertRaises(ValueError):
                clova.response(cek.Message("Hola", lang))
            with self.assertRaises(ValueError):
                Clova(application_id="", default_language=lang, debug_mode=True)


if __name__ == '__main__':
    unittest.main()
