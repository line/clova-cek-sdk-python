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

REQUEST_BODY = b'{"version":"1.0","session":{"sessionId":"73ed88b7-5219-4ca0-9467-e44f852cafc1","user":{"userId":"as-CA80nSomiFI-LAg2u6w","accessToken":"5cc2949c-900c-48a0-a31b-c9544a042377"},"new":true},"context":{"System":{"user":{"userId":"as-CA80nSomiFI-LAg2u6w","accessToken":"5cc2949c-900c-48a0-a31b-c9544a042377"},"device":{"deviceId":"1c62230d-af17-47c5-941b-07ec252c22a4","display":{"size":"l100","orientation":"landscape","dpi":96,"contentLayer":{"width":640,"height":360}}}}},"request":{"type":"IntentRequest","intent":{"name":"Clova.GuideIntent","slots":null}}}'
REQUEST_SIGNATURE = 'rXQ9Bs4Ngj79ZjcjgcQRPc2YUOD+H+U5CV3NnFdKneCXfYLN8hy0PrAj+H0j38BSIeWU6wHJTQf+xEO0xBDuNXbG/hlnQsy2kOFg8U7D2wfopSJ2Tgn/65AmaRs1CSpxRDoLrDyd0kHsLzNfs6MVlb/t+qvOf6WdMo24Ad4f04wtQxd7sS/SWFMNIXdty8VolviYnAjENYPV+bUm4DesJYjBSMLRZcUrAAfNIq+frD25IGAR3Nry85F0DmCLJPk4UgWI/IeKTGsyrkJe+/oH7m6ymkNZRiVxDzEkQgtoD9Vtv2HAiL3B/G95BTWIz4CBZWw6CNsSkrqmjR2VxFMVrw=='

WRONG_REQUEST_BODY = b'{"version":"1.0","session":{"sessionId":"83ed88b7-5219-4ca0-9467-e44f852cafc1","user":{"userId":"as-CA80nSomiFI-LAg2u6w","accessToken":"5cc2949c-900c-48a0-a31b-c9544a042377"},"new":true},"context":{"System":{"user":{"userId":"as-CA80nSomiFI-LAg2u6w","accessToken":"5cc2949c-900c-48a0-a31b-c9544a042377"},"device":{"deviceId":"1c62230d-af17-47c5-941b-07ec252c22a4","display":{"size":"l100","orientation":"landscape","dpi":96,"contentLayer":{"width":640,"height":360}}}}},"request":{"type":"IntentRequest","intent":{"name":"Clova.GuideIntent","slots":null}}}'
WRONG_REQUEST_SIGNATURE = 'sXQ9Bs4Ngj79ZjcjgcQRPc2YUOD+H+U5CV3NnFdKneCXfYLN8hy0PrAj+H0j38BSIeWU6wHJTQf+xEO0xBDuNXbG/hlnQsy2kOFg8U7D2wfopSJ2Tgn/65AmaRs1CSpxRDoLrDyd0kHsLzNfs6MVlb/t+qvOf6WdMo24Ad4f04wtQxd7sS/SWFMNIXdty8VolviYnAjENYPV+bUm4DesJYjBSMLRZcUrAAfNIq+frD25IGAR3Nry85F0DmCLJPk4UgWI/IeKTGsyrkJe+/oH7m6ymkNZRiVxDzEkQgtoD9Vtv2HAiL3B/G95BTWIz4CBZWw6CNsSkrqmjR2VxFMVrw=='
