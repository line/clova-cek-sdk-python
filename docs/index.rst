.. clova-cek-sdk documentation master file, created by
   sphinx-quickstart on Fri Jun 22 12:24:00 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Clova Extension Kit SDK for Python
==================================

This is a python library to simplify the use of the Clova Extensions Kit (CEK). If you want to create your own service, you first need to create your own Extension.
https://clova-developers.line.me/

.. automodule:: cek

Quick start
===========

1. Create a :class:`cek.clova.Clova` instance.

.. code-block:: python

  import os
  from cek import Clova

  # application_id is used to verify requests.
  application_id = os.environ.get("APPLICATION_ID")
  # Set debug_mode=True if you are testing your extension. If True, this disables request verification
  clova = Clova(application_id=application_id, default_language="ja", debug_mode=False)


2. Define request handlers for CEK (on LaunchRequest, IntentRequest, etc).

.. code-block:: python

  @clova.handle.launch
  def launch_request_handler(clova_request):
      return clova.response("こんにちは世界。スキルを起動します")

  @clova.handle.default
  def default_handler(clova_request):
      return clova.response("もう一度お願いします")


3. Setup a web API endpoint. Use :meth:`cek.clova.Clova.route` to route requests.

.. code-block:: python3

  from flask import Flask, request, jsonify

  app = Flask(__name__)

  @app.route('/app', methods=['POST'])
  def my_service():
      resp = clova.route(request.data, request.headers)
      resp = jsonify(resp)
      # make sure we have correct Content-Type that CEK expects
      resp.headers['Content-Type'] = 'application/json;charset-UTF-8'
      return resp

4. Save as ``app.py`` and run app

.. code-block:: shell

  FLASK_APP=app.py flask run


For a detailed example, see `cek-home-python`_ example extension.
See also the API documentation to know how to use the SDK.

.. _`cek-home-python`: https://git.linecorp.com/vogel-frederik/cek-home-python

.. toctree::
   :maxdepth: 2
   :caption: References

   core
   clova

.. toctree::
  :maxdepth: 1
  :caption: Meta information

  changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
