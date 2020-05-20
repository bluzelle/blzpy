import os
import json
from flask import Flask, request, abort, Response, jsonify
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from lib.bluzelle import new_client, APIError

load_dotenv()

client = new_client({
    'mnemonic': os.getenv('MNEMONIC', ''),
    'uuid':     os.getenv('UUID', ''),
    'endpoint': os.getenv('ENDPOINT', ''),
    'chain_id':  os.getenv('CHAIN_ID', ''),
    'debug': True,
})

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    msg = str(e)
    if isinstance(e, HTTPException):
        code = e.code
    elif isinstance(e, APIError):
        msg = e.api_error
        code = 400
    return jsonify(msg), code

@app.route("/", methods = ['POST'])
def uat():
    req = request.json
    if not ('method' in req and 'args' in req):
        raise "both method and args are required"

    method = req['method']
    args = req['args']

    if type(args) is not list:
        raise "args should be a list"

    client_method = getattr(client, method)
    if not client_method:
        raise "unknown method %s" % client_method

    return jsonify(client_method(*args))
