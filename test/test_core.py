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
import cek
import json

from data.requests import LAUNCH_REQUEST_BODY, INTENT_REQUEST_BODY, END_REQUEST_BODY, DEFAULT_REQUEST_BODY, GUIDE_REQUEST_BODY, NO_REQUEST_BODY, INTENT_REQUEST_TURN_OFF

speech_builder = cek.SpeechBuilder(default_language="en")
response_builder = cek.ResponseBuilder(default_language="en")
clova_handler = cek.RequestHandler(application_id="com.line.myApplication", debug_mode=True)
mocked_header = {"": ""}


@clova_handler.launch
def launch_request_handler(launch_request):
    return response_builder.simple_speech_text("Hello! Welcome to My Service!")


@clova_handler.intent("TurnOn")
def turn_on_handler(intent_request):
    response = response_builder.simple_speech_text("Turned on Something")
    plain_text = speech_builder.plain_text("Reprompt Message.")
    response.reprompt = speech_builder.simple_speech(plain_text)
    response.session_attributes = {"LastTurnedOn": "Something"}
    return response


@clova_handler.intent("TurnOff")
def turn_off_handler(intent_request):
    return response_builder.simple_speech_text(message="Turned off Something", end_session=True)


@clova_handler.end
def intent_handler(end_request):
    return response_builder.simple_speech_text("Bye Bye!")


# Handles Build in Intents
@clova_handler.intent("Clova.GuideIntent")
def guide_intent(intent_request):
    attributes = intent_request.session.attributes
    # The session_attributes in the current response will become session_attributes in the next request
    message = "I can switch things off and on!"
    if 'HasExplainedService' in attributes:
        message = "I just explained you what i can do!"

    response = response_builder.simple_speech_text(message)
    response.session_attributes = {'HasExplainedService': True}

    return response


@clova_handler.intent("Clova.CancelIntent")
def cancel_intent(intent_request):
    return response_builder.simple_speech_text(message="Action canceled!", end_session=True)


@clova_handler.intent("Clova.YesIntent")
def yes_intent(intent_request):
    return response_builder.simple_speech_text("Yes, thats good!")


@clova_handler.intent("Clova.NoIntent")
def no_intent(intent_request):
    return response_builder.simple_speech_text(message="はい、わかりました！", language="ja")


# In case no intent could be matched
@clova_handler.default
def default_handler(clova_request):
    return response_builder.simple_speech_text("Sorry I dont understand!")


class Test_Clova(unittest.TestCase):

    def test_launch_handler(self):
        response_dict = clova_handler.route_request(request_body=LAUNCH_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Hello! Welcome to My Service!')

    def test_intent_handler(self):
        response_dict = clova_handler.route_request(request_body=INTENT_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Turned on Something')

    def test_end_session(self):
        response_dict = clova_handler.route_request(request_body=INTENT_REQUEST_TURN_OFF,
                                                    request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']
        should_end_session = response_dict['response']['shouldEndSession']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Turned off Something')
        self.assertEqual(should_end_session, True)

    def test_reprompt(self):
        response_dict = clova_handler.route_request(request_body=INTENT_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['reprompt']['outputSpeech']
        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Reprompt Message.')

    def test_set_attributes(self):
        response_dict = clova_handler.route_request(request_body=INTENT_REQUEST_BODY, request_header_dict=mocked_header)
        self.assertEqual(response_dict['sessionAttributes']['LastTurnedOn'], 'Something')

    def test_end_handler(self):
        response_dict = clova_handler.route_request(request_body=END_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Bye Bye!')

    def test_no_handler(self):
        response_dict = clova_handler.route_request(request_body=NO_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'はい、わかりました！')
        self.assertEqual(output_speech['values']['lang'], 'ja')

    def test_guide_handler(self):
        response_dict = clova_handler.route_request(request_body=GUIDE_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']
        has_explained_service = response_dict['sessionAttributes']['HasExplainedService']

        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertTrue(has_explained_service)
        self.assertEqual(output_speech['values']['value'], 'I can switch things off and on!')

    def test_default_handler(self):
        response_dict = clova_handler.route_request(request_body=DEFAULT_REQUEST_BODY, request_header_dict=mocked_header)
        output_speech = response_dict['response']['outputSpeech']
        self.assertEqual(output_speech['type'], 'SimpleSpeech')
        self.assertEqual(output_speech['values']['value'], 'Sorry I dont understand!')

    def test_default_language(self):
        ja_builder = cek.ResponseBuilder(default_language="ja")
        en_builder = cek.ResponseBuilder(default_language="en")
        response_japanese = ja_builder.simple_speech_text(message="日本語")
        response_english = en_builder.simple_speech_text(message="English")
        # explicit language arg
        response_japanese2x = en_builder.simple_speech_text(message="日本語", language="ja")

        japanese = response_japanese['response']['outputSpeech']['values']['lang']
        japanese2x = response_japanese2x['response']['outputSpeech']['values']['lang']
        english = response_english['response']['outputSpeech']['values']['lang']

        self.assertEqual(japanese, 'ja')
        self.assertEqual(japanese2x, 'ja')
        self.assertEqual(english, 'en')

    def test_application_id_verification(self):
        body_string = LAUNCH_REQUEST_BODY.decode("utf-8")
        request_dict = json.loads(body_string)
        request = cek.Request(request_dict)

        try:
            request.verify_application_id("com.line.myApplication")
        except Exception:
            self.fail("Test for application_id_verification failed!")

    def test_wrong_application_id_verification(self):
        body_string = LAUNCH_REQUEST_BODY.decode("utf-8")
        request_dict = json.loads(body_string)
        request = cek.Request(request_dict)

        with self.assertRaises(cek.ApplicationIdMismatch):
            request.verify_application_id("com.line.wrongApplication")

    def test_wrong_language(self):
        # Test builders
        for lang in ["es", "jp"]:
            with self.assertRaises(ValueError):
                cek.ResponseBuilder(default_language=lang)
            with self.assertRaises(ValueError):
                cek.SpeechBuilder(default_language=lang)

        speech_builder = cek.SpeechBuilder("ja")
        response_builder = cek.ResponseBuilder("ja")
        # Test builder methods
        with self.assertRaises(ValueError):
            speech_builder.plain_text("Hola", language="es")
        with self.assertRaises(ValueError):
            response_builder.simple_speech_text("Hola", language="es")


if __name__ == '__main__':
    unittest.main()
