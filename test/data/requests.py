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

LAUNCH_REQUEST_BODY = b"""{
  "context": {
    "System": {
      "application": {
        "applicationId": "com.line.myApplication"
      },
      "device": {
        "deviceId": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "display": {
          "contentLayer": {
            "height": 0,
            "width": 0
          },
          "size": "none"
        }
      },    
      "user": {
        "userId": "U081234567890abcdef1234567890abcd"
      }
    }
  },
  "request": {
    "event": {
      "name": "",
      "namespace": "",
      "payload": {}
    },
    "extensionId": "com.line.myApplication",
    "intent": {
      "intent": "",
      "name": "",
      "slots": {}
    },
    "locale": "ja-JP",
    "requestId": "12345678-aaaa-bbbb-cccc-1234567890ab",
    "timestamp": "2018-04-04T04:04:04Z",
    "type": "LaunchRequest"
  },
  "session": {
    "new": true,
    "sessionAttributes": {},
    "sessionId": "00000000-0000-0000-0000-000000000000",
    "user": {
      "userId": "U081234567890abcdef1234567890abcd"
    }
  },
  "version": "1.0"
}"""

END_REQUEST_BODY = b"""{
  "context": {
    "System": {
      "application": {
        "applicationId": "com.line.myApplication"
      },
      "device": {
        "deviceId": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "display": {
          "contentLayer": {
            "height": 0,
            "width": 0
          },
          "size": "none"
        }
      },
      "user": {
        "userId": "U081234567890abcdef1234567890abcd"
      }
    }
  },
  "request": {
    "extensionId": "com.line.myApplication",
    "intent": {
      "intent": "",
      "name": "",
      "slots": {}
    },
    "locale": "ja-JP",
    "requestId": "12345678-aaaa-bbbb-cccc-1234567890ab",
    "timestamp": "2018-04-04T04:04:04Z",
    "type": "SessionEndedRequest"
  },
  "session": {
    "new": true,
    "sessionAttributes": {},
    "sessionId": "00000000-0000-0000-0000-000000000000",
    "user": {
      "userId": "U081234567890abcdef1234567890abcd"
    }
  },
  "version": "1.0"
}"""

EVENT_REQUEST_BODY = b"""{
  "context": {
    "System": {
      "application": {
        "applicationId": "com.line.myApplication"
      },
      "device": {
        "deviceId": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "display": {
          "contentLayer": {
            "height": 0,
            "width": 0
          },
          "size": "none"
        }
      },
      "user": {
        "userId": "U081234567890abcdef1234567890abcd"
      }
    }
  },
  "request": {
    "event": {
      "name": "SkillDisabled",
      "namespace": "ClovaSkill",
      "payload": null
    },
    "requestId": "12345678-aaaa-bbbb-cccc-1234567890ab",
    "timestamp": "2018-04-04T04:04:04Z",
    "type": "EventRequest"
  },
  "session": {
    "new": true,
    "sessionAttributes": {},
    "sessionId": "00000000-0000-0000-0000-000000000000",
    "user": {
      "userId": "U081234567890abcdef1234567890abcd"
    }
  },
  "version": "1.0"
}"""


EVENT_REQUEST_BODY_SKILL_ENABLED_FROM_SKILL_STORE = b"""{
  "context": {
    "System": {
      "application": {
        "applicationId": "com.line.myApplication"
      },
      "device": {
        "deviceId": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "display": {
          "contentLayer": {
            "height": 0,
            "width": 0
          },
          "size": "none"
        }
      },
      "user": {
        "userId": "U081234567890abcdef1234567890abcd"
      }
    }
  },
  "request": {
    "event": {
      "name": "SkillEnabled",
      "namespace": "ClovaSkill",
      "payload": null
    },
    "requestId": "12345678-aaaa-bbbb-cccc-1234567890ab",
    "timestamp": "2018-04-04T04:04:04Z",
    "type": "EventRequest"
  },
  "session": null,
  "version": "1.0"
}"""

INTENT_REQUEST_BODY = b"""
{
    "version": "1.0",
    "session": {
        "sessionId": "55555555-5555-5555-5555-555555555555",
        "user": {
            "userId": "1111111111111111111111",
            "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        },
        "new": true
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "com.line.myApplication"
            },
            "user": {
                "userId": "1111111111111111111111",
                "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            },
            "device": {
                "deviceId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                "display": {
                    "size": "l100",
                    "orientation": "landscape",
                    "dpi": 96,
                    "contentLayer": {
                        "width": 640,
                        "height": 360
                    }
                }
            }
        }
    },
    "request": {
        "type": "IntentRequest",
        "intent": {
            "name": "TurnOn",
            "slots": {
                "AirCon": {
                    "name": "AirCon",
                    "value": "Air Conditioner"
                },
                "Light": {
                    "name": "Light",
                    "value": "\xe9\x9b\xbb\xe6\xb0\x97"
                }
            }
        }
    }
}
"""

INTENT_REQUEST_TURN_OFF = b"""
{
    "version": "1.0",
    "session": {
        "sessionId": "55555555-5555-5555-5555-555555555555",
        "user": {
            "userId": "1111111111111111111111",
            "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        },
        "new": true
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "com.line.myApplication"
            },
            "user": {
                "userId": "1111111111111111111111",
                "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            },
            "device": {
                "deviceId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                "display": {
                    "size": "l100",
                    "orientation": "landscape",
                    "dpi": 96,
                    "contentLayer": {
                        "width": 640,
                        "height": 360
                    }
                }
            }
        }
    },
    "request": {
        "type": "IntentRequest",
        "intent": {
            "name": "TurnOff",
            "slots": {}
        }
    }
}
"""

NO_REQUEST_BODY = b"""
{
   "version":"1.0",
   "session":{
      "new": false,
      "sessionAttributes":{},
      "sessionId": "55555555-5555-5555-5555-555555555555",
      "user":{
         "userId": "1111111111111111111111"
      }
   },
   "context":{
      "System":{
         "application":{
            "applicationId":"com.line.myApplication"
         },
         "device":{
            "deviceId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
            "display":{
               "size":"none",
               "contentLayer":{
                  "width":0,
                  "height":0
               }
            }
         },
         "user":{
            "userId":"1111111111111111111111"
         }
      }
   },
   "request":{
      "type":"IntentRequest",
      "requestId": "12345678-aaaa-bbbb-cccc-1234567890ab",
      "timestamp":"2018-05-01T10:23:45Z",
      "locale":"ja-JP",
      "extensionId":"com.line.myApplication",
      "intent":{
         "intent":"Clova.NoIntent",
         "name":"Clova.NoIntent",
         "slots":{}
      },
      "event":{
         "namespace":"",
         "name":"",
         "payload":{}
      }
   }
}
"""

GUIDE_REQUEST_BODY = b"""
{
    "version": "1.0",
    "session": {
        "sessionId": "55555555-5555-5555-5555-555555555555",
        "user": {
            "userId": "1111111111111111111111",
            "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        },
        "new": true
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "com.line.myApplication"
            },
            "user": {
                "userId": "1111111111111111111111",
                "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            },
            "device": {
                "deviceId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                "display": {
                    "size": "l100",
                    "orientation": "landscape",
                    "dpi": 96,
                    "contentLayer": {
                        "width": 640,
                        "height": 360
                    }
                }
            }
        }
    },
    "request": {
        "type": "IntentRequest",
        "intent": {
            "name": "Clova.GuideIntent",
            "slots": {}
        }
    }
}
"""


AUDIOPLAYER_EVENT_REQUEST_BODY = b"""
{
    "version": "1.0",
    "session": {
        "sessionId": "55555555-5555-5555-5555-555555555555",
        "user": {
            "userId": "1111111111111111111111",
            "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        },
        "new": true
    },
    "context": {
        "AudioPlayer": {
            "offsetInMilliseconds": 12734,
            "playerActivity": "STOPPED",
            "stream": {
                "StreamInfo" : "WIP"
            },
            "totalInMilliseconds": 52734
        },
        "System": {
            "application": {
                "applicationId": "com.line.myApplication"
            },
            "user": {
                "userId": "1111111111111111111111",
                "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            },
            "device": {
                "deviceId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                "display": {
                    "size": "l100",
                    "orientation": "landscape",
                    "dpi": 96,
                    "contentLayer": {
                        "width": 640,
                        "height": 360
                    }
                }
            }
        }
    },
    "request": {
        "type": "EventRequest",
        "requestId": "e5464288-50ff-4e99-928d-4a301e083d41",
        "timestamp": "2017-09-05T05:41:21Z",
        "event": {
            "namespace": "AudioPlayer",
            "name": "PlayStopped",
            "payload": {}
        }
    }
}
"""


DEFAULT_REQUEST_BODY = b"""
{
    "version": "1.0",
    "session": {
        "sessionId": "55555555-5555-5555-5555-555555555555",
        "user": {
            "userId": "1111111111111111111111",
            "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        },
        "new": true
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "com.line.myApplication"
            },
            "user": {
                "userId": "1111111111111111111111",
                "accessToken": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            },
            "device": {
                "deviceId": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                "display": {
                    "size": "l100",
                    "orientation": "landscape",
                    "dpi": 96,
                    "contentLayer": {
                        "width": 640,
                        "height": 360
                    }
                }
            }
        }
    },
    "request": {
        "type": "IntentRequest",
        "intent": {
            "name": "SomeOtherIntent",
            "slots": {
                "Light": {
                    "name": "Light",
                    "value": "\xe9\x9b\xbb\xe6\xb0\x97"
                }
            }
        }
    }
}
"""
