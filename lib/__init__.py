import requests
import json
import base64
import random
import string
from hashlib import sha256
from .mnemonic_utils import mnemonic_to_private_key
from ecdsa import SigningKey, SECP256k1

DEFAULT_ENDPOINT = "http://localhost:1317"
DEFAULT_CHAIN_ID = "bluzelle"
HD_PATH = "m/44'/118'/0'/0/0"
ADDRESS_PREFIX = "bluzelle"
TX_COMMAND = "/txs"
TOKEN_NAME = "ubnt"
PUB_KEY_TYPE = "tendermint/PubKeySecp256k1"


class APIError(Exception):
    pass


class Client:
    def __init__(self, options):
        self.options = options

    def api_query(self, endpoint):
        url = self.options['endpoint'] + endpoint
        self.debug('querying url(%s)...' % (url))
        response = requests.get(url)
        error = self.response_has_error(response)
        if error:
            raise error
        data = response.json()
        self.debug('response (%s)...' % (data))
        return data

    def api_mutate(self, method, endpoint, payload):
        url = self.options['endpoint'] + endpoint
        self.debug('mutating %s(%s)...' % (method, url))
        payload = self.json_dumps(payload)
        self.debug("%s" % payload)
        response = getattr(requests, method)(
            url,
            data=payload,
            headers={"content-type": "application/x-www-form-urlencoded"},
            verify=False
        )
        self.debug("%s" % response.text)
        error = self.response_has_error(response)
        if error:
            raise error
        data = response.json()
        self.debug('response (%s)...' % (data))
        return data

    def read_account(self):
        url = "/auth/accounts/" + self.options["address"]
        return self.api_query(url)['result']['value']

    def read(self, key):
        url = "/crud/read/" + self.options["uuid"] + "/" + key
        return self.api_query(url)['result']['value']

    def proven_read(self, key):
        url = "/crud/pread/" + self.options["uuid"] + "/" + key
        return self.api_query(url)['result']['value']

    def create(self, key, value):
        return self.send_transaction({
            "key": key,
            "value": value,
            "api_request_method": "post",
            "api_request_endpoint": "/crud/create"
        })

    def send_transaction(self, args):
        address = self.options['address']
        payload = {
            "BaseReq": {
                "chain_id": self.options['chain_id'],
                "from": address,
            },
            "Key": args['key'],
            "Owner": address,
            "UUID": self.options['uuid'],
            "Value": args['value']
        }
        #  validate transaction
        txn = self.api_mutate(
            args["api_request_method"],
            args["api_request_endpoint"],
            payload
        )['value']

        # set txn memo
        txn['memo'] = make_random_string(32)

        # set txn gas
        fee = txn['fee']
        fee_gas = int(fee['gas'])
        gas_info = self.options['gas_info']
        if gas_info['max_gas'] is not 0 and fee_gas > gas_info['max_gas']:
            fee['gas'] = strconv.Itoa(gas_info['max_gas'])
        if gas_info['max_fee'] is not 0:
            fee['amount'] = [{'denom': TOKEN_NAME, 'amount': str(gas_info['max_fee'])}]
        elif gasInfo.GasPrice is not 0:
            fee['amount'] = [{'denom': TOKEN_NAME, 'amount': str(fee_gas * gas_info['gas_price'])}]
        txn['fee'] = fee

        # sign
        txn['signatures'] = [{
            "pub_key": {
                "type": PUB_KEY_TYPE,
                "value": self.get_pub_key_string()
            },
            "signature": self.sign_transaction(txn),
            "account_number": str(self.account['account_number']),
            "sequence": str(self.account['sequence'])
        }]

        payload = {
            "tx": txn,
            "mode": "block"
        }

        # broadcast
        response = self.api_mutate(
            "post",
            TX_COMMAND,
            payload
        )
        if 'code' in response:
            raise APIError(response['raw_log'])
        if 'data' in response:
            return bytes.fromhex(response['data']).decode("ASCII")

    def sign_transaction(self, txn):
        payload = {
            "account_number": str(self.account['account_number']),
            "chain_id": self.options['chain_id'],
            "fee": txn["fee"],
            "memo": txn["memo"],
            "msgs": txn["msg"],
            "sequence": str(self.account['sequence']),
        }
        payload = bytes(self.json_dumps(payload), 'utf-8')
        return base64.b64encode(self.private_key.sign_deterministic(payload, hashfunc=sha256)).decode("utf-8")

    def response_has_error(self, response):
        error = response.json().get('error', '')
        if error:
            return APIError(error)

    def get_pub_key_string(self):
        return base64.b64encode(self.private_key.verifying_key.to_string("compressed")).decode("utf-8")

    def json_dumps(self, payload):
        return json.dumps(payload, sort_keys=True, separators=(',', ':'))

    def debug(self, log):
        if self.options['debug']:
            print(log)


def new_client(options):
    # validate options
    if not options.get('chain_id', None):
        options['chain_id'] = DEFAULT_CHAIN_ID

    if not options.get('endpoint', None):
        options['endpoint'] = DEFAULT_ENDPOINT

    gas_info = options.get('gas_info', {})
    if not gas_info.get('gas_price', 0):
        gas_info['gas_price'] = 0
    if not gas_info.get('max_fee', 0):
        gas_info['max_fee'] = 0
    if not gas_info.get('max_gas', 0):
        gas_info['max_gas'] = 0
    options['gas_info'] = gas_info

    if not ('debug' in options):
        options['debug'] = False

    client = Client(options)
    client.private_key = SigningKey.from_string(mnemonic_to_private_key(
        options['mnemonic'], str_derivation_path=HD_PATH), curve=SECP256k1)

    # todo: verify address

    client.account = client.read_account()

    return client


def make_random_string(size):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(size))
