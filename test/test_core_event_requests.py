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
from data.requests import EVENT_REQUEST_BODY
from data.requests import EVENT_REQUEST_BODY_FROM_SKILL_STORE


class Test_IntentRequest(unittest.TestCase):

    def setUp(self):
        body_string = EVENT_REQUEST_BODY.decode("utf-8")
        request_dict = json.loads(body_string)
        self.request = cek.Request.create(request_dict)

        body_string = EVENT_REQUEST_BODY_FROM_SKILL_STORE.decode("utf-8")
        request_dict = json.loads(body_string)
        self.request_from_skill_store = cek.Request.create(request_dict)

    def tearDown(self):
        self.request = None

    def test_request_id(self):
        request_id = self.request.id

        self.assertEqual(request_id, '12345678-aaaa-bbbb-cccc-1234567890ab')

    def test_request_event(self):
        event = self.request.event

        self.assertEqual(event.namespace, 'ClovaSkill')
        self.assertEqual(event.name, 'SkillDisabled')
        self.assertIsNone(event.payload)

    def test_request_event_skill_enable_from_skill_store(self):
        event = self.request_from_skill_store.event

        self.assertEqual(event.namespace, 'ClovaSkill')
        self.assertEqual(event.name, 'SkillEnabled')
        self.assertIsNone(event.payload)

    def test_request_timestamp(self):
        timestamp = self.request.timestamp

        self.assertEqual(timestamp, '2018-04-04T04:04:04Z')

    def test_request_context_device(self):
        context = self.request.context
        device = context.device

        self.assertEqual(device.id, "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")


if __name__ == '__main__':
    unittest.main()
