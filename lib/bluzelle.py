import requests
import json
import base64
import random
import string
import logging
import time
import hashlib
import bech32
from .mnemonic_utils import mnemonic_to_private_key
from ecdsa import SigningKey, SECP256k1

DEFAULT_ENDPOINT = "http://localhost:1317"
DEFAULT_CHAIN_ID = "bluzelle"
HD_PATH = "m/44'/118'/0'/0/0"
ADDRESS_PREFIX = "bluzelle"
TX_COMMAND = "/txs"
TOKEN_NAME = "ubnt"
PUB_KEY_TYPE = "tendermint/PubKeySecp256k1"
BROADCAST_MAX_RETRIES = 10
BROADCAST_RETRY_INTERVAL_SECONDS = 1

# client option validation error
class OptionsError(Exception):
    pass

# general api error
class APIError(Exception):
    pass

class Client:
    def __init__(self, options):
        self.options = options

    #

    def read_account(self):
        url = "/auth/accounts/%s" % self.options["address"]
        return self.api_query(url)['result']['value']

    def version(self):
        url = "/node_info"
        return self.api_query(url)['application_version']['version']

    # mutate methods

    def create(self, key, value, lease = 0):
        return self.send_transaction("post", "/crud/create", {
            "Key": key,
            "Lease": str(lease),
            "Value": value,
        })

    def update(self, key, value, lease = None):
        payload = { "Key": key }
        if type(lease) is int:
            payload["Lease"] = str(lease)
        payload["Value"] = value
        return self.send_transaction("post", "/crud/update", payload)

    def delete(self, key):
        return self.send_transaction("delete", "/crud/delete", {
            "Key": key,
        })

    def rename(self, key, new_key):
        return self.send_transaction("post", "/crud/rename", {
            "Key": key,
            "NewKey": new_key,
        })

    def delete_all(self):
        return self.send_transaction("post", "/crud/deleteall", {})

    def multi_update(self, payload):
      list = []
      for key in payload:
        list.append({"key": key, "value": payload[key]})
      return self.send_transaction("post", "/crud/multiupdate", {"KeyValues": list})

    def renew_lease(self, key, lease):
        self.send_transaction("post", "/crud/renewlease", {
            "Key": key,
            "Lease": str(lease),
        })

    def renew_all_leases(self, lease):
        self.send_transaction("post", "/crud/renewleaseall", {
            "Lease": str(lease),
        })

    # query methods

    def read(self, key):
        url = "/crud/read/{uuid}/{key}".format(uuid=self.options["uuid"], key=key)
        return self.api_query(url)['result']['value']

    def proven_read(self, key):
        url = "/crud/pread/{uuid}/{key}".format(uuid=self.options["uuid"], key=key)
        return self.api_query(url)['result']['value']

    def has(self, key):
        url = "/crud/has/{uuid}/{key}".format(uuid=self.options["uuid"], key=key)
        return self.api_query(url)['result']['has']

    def count(self):
        url = "/crud/count/{uuid}".format(uuid=self.options["uuid"])
        return int(self.api_query(url)['result']['count'])

    def keys(self):
        url = "/crud/keys/{uuid}".format(uuid=self.options["uuid"])
        return self.api_query(url)['result']['keys']

    def key_values(self):
        url = "/crud/keyvalues/{uuid}".format(uuid=self.options["uuid"])
        return self.api_query(url)['result']['keyvalues']

    def get_lease(self, key):
        url = "/crud/getlease/{uuid}/{key}".format(uuid=self.options["uuid"], key=key)
        return int(self.api_query(url)['result']['lease'])

    def get_n_shortest_leases(self, n):
        url = "/crud/getnshortestlease/{uuid}/{n}".format(uuid=self.options["uuid"], n=str(n))
        return self.api_query(url)['result']['keyleases']

    #query tx methods
    def tx_read(self, key):
          res = self.send_transaction("post", "/crud/read", {
              "Key": key,
          })
          return res['value']

    def tx_has(self, key):
        res = self.send_transaction("post", "/crud/has", {
            "Key": key,
        })
        return res['has']

    def tx_count(self):
        res = self.send_transaction("post", "/crud/count", {})
        return int(res['count'])

    def tx_keys(self):
        res = self.send_transaction("post", "/crud/keys", {})
        return res['keys']

    def tx_key_values(self):
        res = self.send_transaction("post", "/crud/keyvalues", {})
        return res['keyvalues']

    def tx_get_lease(self, key):
        res = self.send_transaction("post", "/crud/getlease", {
            "Key": key,
        })
        return int(res['lease'])

    def tx_get_n_shortest_leases(self, n):
        res = self.send_transaction("post", "/crud/getnshortestlease", {
            "N": str(n),
        })
        return res['keyleases']

    # api
    def api_query(self, endpoint):
        url = self.options['endpoint'] + endpoint
        self.logger.debug('querying url(%s)...' % (url))
        response = requests.get(url)
        error = self.get_response_error(response)
        if error:
            raise error
        data = response.json()
        self.logger.debug('response (%s)...' % (data))
        return data

    def api_mutate(self, method, endpoint, payload):
        url = self.options['endpoint'] + endpoint
        self.logger.debug('mutating url({url}), method({method})...'.format(url=url, method=method))
        payload = self.json_dumps(payload)
        self.logger.debug("%s" % payload)
        response = getattr(requests, method)(
            url,
            data=payload,
            headers={"content-type": "application/x-www-form-urlencoded"},
            verify=False
        )
        self.logger.debug("%s" % response.text)
        error = self.get_response_error(response)
        if error:
            raise error
        data = response.json()
        self.logger.debug('response (%s)...' % (data))
        return data

    def send_transaction(self, method, endpoint, payload):
        self.broadcast_retries = 0
        txn = self.validate_transaction(method, endpoint, payload)
        return self.broadcast_transaction(txn)

    def validate_transaction(self, method, endpoint, payload):
        address = self.options['address']
        payload.update({
            "BaseReq": {
                "chain_id": self.options['chain_id'],
                "from": address,
            },
            "Owner": address,
            "UUID": self.options['uuid'],
        })
        return self.api_mutate(method, endpoint, payload)['value']

    def broadcast_transaction(self, txn):
        # set txn memo
        txn['memo'] = Client.make_random_string(32)

        # set txn gas
        fee = txn['fee']
        fee_gas = int(fee['gas'])
        gas_info = self.options['gas_info']
        if gas_info['max_gas'] is not 0 and fee_gas > gas_info['max_gas']:
            fee['gas'] = str(gas_info['max_gas'])
        if gas_info['max_fee'] is not 0:
            fee['amount'] = [{'denom': TOKEN_NAME, 'amount': str(gas_info['max_fee'])}]
        elif gasInfo['gas_price'] is not 0:
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
        # this is far from ideal, doesn't match their docs, and is probably going to change (again) in the future.
        if not ('code' in response):
            self.account['sequence'] += 1
            if 'data' in response:
                return json.loads(bytes.fromhex(response['data']).decode("ascii"))
            return

        raw_log = response['raw_log']
        if "signature verification failed" in raw_log:
            self.broadcast_retries += 1
            self.logger.warning("transaction failed ... retrying(%i) ...", self.broadcast_retries)
            if self.broadcast_retries >= BROADCAST_MAX_RETRIES:
                raise APIError("transaction failed after max retry attempts")
            time.sleep(BROADCAST_RETRY_INTERVAL_SECONDS)
            # lookup changed sequence
            self.set_account()
            return self.broadcast_transaction(txn)

        raise APIError(raw_log)

    def sign_transaction(self, txn):
        payload = {
            "account_number": str(self.account['account_number']),
            "chain_id": self.options['chain_id'],
            "fee": txn["fee"],
            "memo": txn["memo"],
            "msgs": txn["msg"],
            "sequence": str(self.account['sequence']),
        }
        payload = self.json_dumps(payload)
        self.logger.debug("sign %s" % payload)
        payload = bytes(payload, 'utf-8')
        return base64.b64encode(self.private_key.sign_deterministic(payload, hashfunc=hashlib.sha256)).decode("utf-8")

    def set_account(self):
        self.account = self.read_account()

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

    def setup_logging(self):
        logger = logging.getLogger('bluzelle')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.disabled = not self.options['debug']
        self.logger = logger

    def set_private_key(self):
        self.private_key = SigningKey.from_string(
            mnemonic_to_private_key(self.options['mnemonic'], str_derivation_path=HD_PATH),
            curve=SECP256k1
        )

    def verify_address(self):
        pk = self.private_key.verifying_key.to_string("compressed")

        h = hashlib.new('sha256')
        h.update(pk)
        s = h.digest()

        h = hashlib.new('ripemd160')
        h.update(s)
        r = h.digest()

        address = bech32.bech32_encode(ADDRESS_PREFIX, bech32.convertbits(r, 8, 5, True))
        if address != self.options['address']:
            raise OptionsError('bad credentials(verify your address and mnemonic)')


# initialize new client with provided `options`
# @param options
#   @required address
#   @required mnemonic
#   @optional chain_id
#   @optional endpoint
#   @optional gas_info
#   @optional debug
def new_client(options):
    # validate options
    if not ('address' in options):
        raise OptionsError('address is required')

    if not ('mnemonic' in options):
        raise OptionsError('mnemonic is required')

    gas_info = options.get('gas_info', {})
    if type(gas_info) is not dict:
        raise OptionsError('gas_info should be a dict of {gas_price, max_fee, max_gas}')
    gas_info_keys = ["gas_price", "max_fee", "max_gas"]
    for k in gas_info_keys:
        v = gas_info.get(k, 0)
        if type(v) is not int:
            raise OptionsError('gas_info[%s] should be an int' % k)
        gas_info[k] = v

    if not ('debug' in options):
        options['debug'] = False

    if not options.get('chain_id', None):
        options['chain_id'] = DEFAULT_CHAIN_ID

    if not options.get('endpoint', None):
        options['endpoint'] = DEFAULT_ENDPOINT

    client = Client(options)

    # logging
    client.setup_logging()

    # private key
    client.set_private_key()

    # verify address
    client.verify_address()

    # account
    client.set_account()

    return client
