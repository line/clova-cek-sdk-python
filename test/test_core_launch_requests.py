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
import logging
import cek
import json

from data.requests import LAUNCH_REQUEST_BODY

logging.disable(logging.CRITICAL)


class Test_LaunchRequest(unittest.TestCase):

    def setUp(self):
        body_string = LAUNCH_REQUEST_BODY.decode("utf-8")
        request_dict = json.loads(body_string)
        self.request = cek.Request.create(request_dict)

    def tearDown(self):
        self.request = None

    def test_request_type(self):
        request_type = self.request.type

        self.assertEqual(request_type, 'LaunchRequest')

    def test_user_id(self):
        user_id = self.request.session.user.id

        self.assertEqual(user_id, "U081234567890abcdef1234567890abcd")

    def test_session_id(self):
        session_id = self.request.session.id
        self.assertEqual(session_id, "00000000-0000-0000-0000-000000000000")


if __name__ == '__main__':
    unittest.main()
