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

from cryptography.exceptions import InvalidSignature
from data.example_request import REQUEST_BODY, REQUEST_SIGNATURE, WRONG_REQUEST_BODY, WRONG_REQUEST_SIGNATURE


class Test_Signature(unittest.TestCase):

    def test_signature(self):
        signature_base64 = REQUEST_SIGNATURE
        body = REQUEST_BODY

        clova_handler = cek.RequestHandler(application_id="")

        request_header = {"Signaturecek": signature_base64}
        try:
            clova_handler._verify_request(request_body=body, request_header_dict=request_header)
        except InvalidSignature:
            self.fail("_verify_request() failed!")

    def test_signature_wrong_body(self):
        signature_base64 = REQUEST_SIGNATURE
        body = WRONG_REQUEST_BODY

        clova_handler = cek.RequestHandler(application_id="")
        request_header = {"Signaturecek": signature_base64}

        with self.assertRaises(InvalidSignature):
            clova_handler._verify_request(request_body=body,
                                          request_header_dict=request_header)

    def test_signature_wrong_signature(self):
        signature_base64 = WRONG_REQUEST_SIGNATURE
        body = REQUEST_BODY

        clova_handler = cek.RequestHandler(application_id="")
        request_header = {"Signaturecek": signature_base64}

        with self.assertRaises(InvalidSignature):
            clova_handler._verify_request(request_body=body,
                                          request_header_dict=request_header)
