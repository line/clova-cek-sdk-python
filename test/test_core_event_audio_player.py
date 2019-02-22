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
from data.requests import AUDIOPLAYER_EVENT_REQUEST_BODY


class Test_IntentRequest(unittest.TestCase):

    def setUp(self):
        body_string = AUDIOPLAYER_EVENT_REQUEST_BODY.decode("utf-8")
        request_dict = json.loads(body_string)
        self.request = cek.Request.create(request_dict)

    def tearDown(self):
        self.request = None

    def test_request_id(self):
        request_id = self.request.id

        self.assertEqual(request_id, 'e5464288-50ff-4e99-928d-4a301e083d41')

    def test_request_event(self):
        event = self.request.event

        self.assertEqual(event.namespace, 'AudioPlayer')
        self.assertEqual(event.name, 'PlayStopped')
        self.assertTrue(len(event.payload) == 0)

    def test_request_timestamp(self):
        timestamp = self.request.timestamp

        self.assertEqual(timestamp, '2017-09-05T05:41:21Z')

    def test_request_context_player(self):
        context = self.request.context
        player = context.audio_player

        self.assertEqual(player.offset, 12734)
        self.assertEqual(player.total, 52734)
        self.assertEqual(player.activity, "STOPPED")

    def test_request_context_device(self):
        context = self.request.context
        device = context.device

        self.assertEqual(device.id, "dddddddd-dddd-dddd-dddd-dddddddddddd")


if __name__ == '__main__':
    unittest.main()
