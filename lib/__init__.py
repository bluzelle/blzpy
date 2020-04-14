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

    # methods
    def read_account(self):
        url = "/auth/accounts/%s" % self.options["address"]
        return self.api_query(url)['result']['value']

    def read(self, key):
        url = "/crud/read/{uuid}/{key}".format(uuid=self.options["uuid"], key=key)
        return self.api_query(url)['result']['value']

    def proven_read(self, key):
        url = "/crud/pread/{uuid}/{key}".format(uuid=self.options["uuid"], key=key)
        return self.api_query(url)['result']['value']

    def create(self, key, value):
        return self.send_transaction("post", "/crud/create", {
            "Key": key,
            "Value": value,
        })

    def update(self, key, value):
        return self.send_transaction("post", "/crud/update", {
            "Key": key,
            "Value": value,
        })

    def delete(self, key):
        return self.send_transaction("delete", "/crud/delete", {
            "Key": key,
        })

    # api
    def api_query(self, endpoint):
        url = self.options['endpoint'] + endpoint
        self.debug('querying url(%s)...' % (url))
        response = requests.get(url)
        error = self.get_response_error(response)
        if error:
            raise error
        data = response.json()
        self.debug('response (%s)...' % (data))
        return data

    def api_mutate(self, method, endpoint, payload):
        url = self.options['endpoint'] + endpoint
        self.debug('mutating url({url}), method({method})...'.format(url=url, method=method))
        payload = self.json_dumps(payload)
        self.debug("%s" % payload)
        response = getattr(requests, method)(
            url,
            data=payload,
            headers={"content-type": "application/x-www-form-urlencoded"},
            verify=False
        )
        self.debug("%s" % response.text)
        error = self.get_response_error(response)
        if error:
            raise error
        data = response.json()
        self.debug('response (%s)...' % (data))
        return data

    def send_transaction(self, method, endpoint, payload):
        address = self.options['address']
        payload.update({
            "BaseReq": {
                "chain_id": self.options['chain_id'],
                "from": address,
            },
            "Owner": address,
            "UUID": self.options['uuid'],
        })
        #  validate transaction
        txn = self.api_mutate(method, endpoint, payload)['value']

        # set txn memo
        txn['memo'] = Client.make_random_string(32)

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

        # broadcast
        payload = {
            "tx": txn,
            "mode": "block"
        }
        response = self.api_mutate(
            "post",
            TX_COMMAND,
            payload
        )

        # https://github.com/bluzelle/blzjs/blob/45fe51f6364439fa88421987b833102cc9bcd7c0/src/swarmClient/cosmos.js#L240-L246
        # note - as of right now (3/6/20) the responses returned by the Cosmos REST interface now look like this:
        # success case: {"height":"0","txhash":"3F596D7E83D514A103792C930D9B4ED8DCF03B4C8FD93873AB22F0A707D88A9F","raw_log":"[]"}
        # failure case: {"height":"0","txhash":"DEE236DEF1F3D0A92CB7EE8E442D1CE457EE8DB8E665BAC1358E6E107D5316AA","code":4,
        #  "raw_log":"unauthorized: signature verification failed; verify correct account sequence and chain-id"}
        #
        # This is far from ideal, doesn't match their docs, and is probably going to change (again) in the future.

        if 'data' in response:
            self.account['sequence'] += 1
            return bytes.fromhex(response['data']).decode("ascii")
        if 'code' in response:
            raise APIError(response['raw_log'])

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

    def get_response_error(self, response):
        error = response.json().get('error', '')
        if error:
            return APIError(error)

    def get_pub_key_string(self):
        return base64.b64encode(self.private_key.verifying_key.to_string("compressed")).decode("utf-8")

    def json_dumps(self, payload):
        return json.dumps(payload, sort_keys=True, separators=(',', ':'))

    @classmethod
    def make_random_string(cls, size):
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(size))

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

    # private key
    client.private_key = SigningKey.from_string(
        mnemonic_to_private_key(options['mnemonic'], str_derivation_path=HD_PATH),
        curve=SECP256k1
    )

    # verify address (todo)

    # account
    client.account = client.read_account()

    return client
