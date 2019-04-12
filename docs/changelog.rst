Change log
==========

1.0.0 <2018-08-03>
------------------

* Initial release

1.0.1 <2018-09-19>
------------------
* BugFix: Simple response does not end session

1.1.0 <2019-04-11>
------------------

This update contains some refactoring of the Request class into subclasses of different Request types to better reflect the request definitions.

* Added and refactored requests into `LaunchRequest`, `SessionEndedRequest`, `IntentRequest` and `EventRequest`
* Refactored core module into `models` and `handler`
* `verify_application_id` can throw `ApplicationIdMismatch`
* Renamed `EndRequest` -> `SessionEndedRequest`
* Added `Event`, `User`, `AudioPlayer`, `Context`, `Device`, and `Session` Model

Breaking API changes are:

* request.request_type -> request.type
* request.session_id -> request.session.id
* request.session_attributes -> request.session.attributes
* request.access_token -> request.session.user.access_token
* request.intent_name -> intent_request.name
