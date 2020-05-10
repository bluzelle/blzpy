import os
import json
from flask import Flask, request, abort, Response, jsonify
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from lib.bluzelle import new_client

load_dotenv()

client = new_client({
    'address':  os.getenv('ADDRESS', ''),
    'mnemonic': os.getenv('MNEMONIC', ''),
    'uuid':     os.getenv('UUID', ''),
    'endpoint': os.getenv('ENDPOINT', ''),
    'chain_id':  os.getenv('CHAIN_ID', ''),
    'gas_info': {
        'max_fee': 4000001,
    },
    'debug': True,
})

app = Flask(__name__)

def error(msg):
    return abort(400, msg)

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

@app.route("/", methods = ['POST'])
def uat():
    req = request.json
    if not ('method' in req and 'args' in req):
        return error("both method and args are required")

    method = req['method']
    args = req['args']

    if type(args) is not list:
        return error("args should be a list")

    client_method = getattr(client, method)
    if not client_method:
        return error("unknown method %s" % client_method)

    return jsonify(client_method(*args) or '')
