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
from data.requests import INTENT_REQUEST_BODY


class Test_IntentRequest(unittest.TestCase):

    def setUp(self):
        body_string = INTENT_REQUEST_BODY.decode("utf-8")
        request_dict = json.loads(body_string)

        self.request = cek.Request(request_dict)

    def tearDown(self):
        self.request = None

    def test_request_type(self):
        request_type = self.request.request_type

        self.assertEqual(request_type, 'IntentRequest')

    def test_intent_name(self):
        intent_name = self.request.intent_name

        self.assertEqual(intent_name, "TurnOn")

    def test_request_is_intent(self):
        is_intent = self.request.is_intent

        self.assertTrue(is_intent)

    def test_user_id(self):
        user_id = self.request.user_id

        self.assertEqual(user_id, "1111111111111111111111")

    def test_session_id(self):
        session_id = self.request.session_id

        self.assertEqual(session_id, "55555555-5555-5555-5555-555555555555")

    def test_request_returns_slot_value(self):
        value = self.request.slot_value("Light")

        self.assertEqual(value, u"電気")

    def test_slots(self):
        slots = self.request.slots_dict
        if "Light" in slots:
            light_value = slots["Light"]

        expected_slots = {'AirCon': 'Air Conditioner', 'Light': u'電気'}
        expected_light_value = u'電気'
        self.assertEqual(slots, expected_slots)
        self.assertEqual(light_value, expected_light_value)




if __name__ == '__main__':
    unittest.main()
