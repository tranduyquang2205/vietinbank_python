import requests
import json
import random
from base64 import b64encode
import re
import json
import string
from datetime import datetime
class VTB:
    def __init__(self, username, password, account_number):
        self.url = {
            'captcha': 'https://api-ipay.vietinbank.vn/api/get-captcha/',
            'login': 'https://api-ipay.vietinbank.vn/ipay/wa/signIn',
            'getCustomerDetails': 'https://api-ipay.vietinbank.vn/ipay/wa/getCustomerDetails',
            'getEntitiesAndAccounts': 'https://api-ipay.vietinbank.vn/ipay/wa/getEntitiesAndAccounts',
            'getCmsData': 'https://api-ipay.vietinbank.vn/ipay/wa/getCmsData',
            'getBillPayees': 'https://api-ipay.vietinbank.vn/ipay/wa/getBillPayees',
            'creditAccountList': 'https://api-ipay.vietinbank.vn/ipay/wa/creditAccountList',
            'getAvgAccountBal': 'https://api-ipay.vietinbank.vn/ipay/wa/getAvgAccountBal',
            'getHistTransactions': 'https://api-ipay.vietinbank.vn/ipay/wa/getHistTransactions',
            'getAccountDetails': 'https://api-ipay.vietinbank.vn/ipay/wa/getAccountDetails',
            'getCodeMapping': 'https://api-ipay.vietinbank.vn/ipay/wa/getCodeMapping',
            'napasTransfer': 'https://api-ipay.vietinbank.vn/ipay/wa/napasTransfer',
            'makeInternalTransfer': 'https://api-ipay.vietinbank.vn/ipay/wa/makeInternalTransfer',
            'getPayees': 'https://api-ipay.vietinbank.vn/ipay/wa/getPayees',
            'authenSoftOtp': 'https://api-ipay.vietinbank.vn/ipay/wa/authenSoftOtp'
        }
        self.browser_info = "Chrome-98.04758102"
        self.lang = 'vi'
        self.client_info = '127.0.0.1;MacOSProMax'
        self.timeout = 15
        self.public_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLenQHmHpaqYX4IrRVM8H1uB21\nxWuY+clsvn79pMUYR2KwIEfeHcnZFFshjDs3D2ae4KprjkOFZPYzEWzakg2nOIUV\nWO+Q6RlAU1+1fxgTvEXi4z7yi+n0Zs0puOycrm8i67jsQfHi+HgdMxCaKzHvbECr\n+JWnLxnEl6615hEeMQIDAQAB\n-----END PUBLIC KEY-----"
        self.session_id = None
        self.account_number = account_number
        self.ipay_id = None
        self.token_id = None
        self.username = username
        self.access_code = password
        self.captcha_code = None
        self.captcha_id = None
        self.request_id = None
        self.sign = None
        self.customer_number = None
        self.bsb = None
        self.account_type = None
        self.currency_code = None

    def save_data(self):
        data = {
            'username': self.username,
            'password': self.access_code,
            'accountNumber': self.account_number,
            'sessionId': self.session_id,
            'ipayId': self.ipay_id,
            'tokenId': self.token_id,
            'customerNumber': self.customer_number,
            'currencyCode': self.currency_code,
            'bsb': self.bsb,
            'accountType': self.account_type,
        }
        with open(f"data/{self.username}.json", "w") as file:
            json.dump(data, file)

    def parse_data(self):
        try:
            with open(f"data/{self.username}.json", "r") as file:
                data = json.load(file)
                self.username = data['username']
                self.access_code = data['password']
                self.access_code = data['password']
                self.account_number = data.get('accountNumber', '')
                self.account_type = data.get('accountType', '')
                self.customer_number = data.get('customerNumber', '')
                self.bsb = data.get('bsb', '')
                self.token_id = data.get('tokenId', '')
                self.ipay_id = data.get('ipayId', '')
                self.session_id = data.get('sessionId', '')
                self.currency_code = data.get('currencyCode', '')
        except FileNotFoundError:
            pass

    def get_captcha(self):
        self.captcha_id = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=9))
        headers = self.header_null()
        response = requests.get(self.url['captcha'] + self.captcha_id, headers=headers, timeout=self.timeout)
        svg = response.text
        self.captcha_code = self.bypass_captcha(svg)
        return True

    def do_login(self):
        self.request_id = self.generate_request_id()
        self.get_captcha()
        params = {
            'accessCode': self.access_code,
            'browserInfo': self.browser_info,
            'captchaCode': self.captcha_code,
            'captchaId': self.captcha_id,
            'clientInfo': self.client_info,
            'lang': self.lang,
            'requestId': self.request_id,
            'userName': self.username,
            'screenResolution': "1201x344"
        }
        
        headers = self.header_null()
        body = self.make_body_request_json(params)
        response = requests.post(self.url['login'], headers=headers, data=body, timeout=self.timeout)
        login = response.json()
        print(login)
        if not login['error']:
            self.session_id = login['sessionId']
            self.customer_number = login['customerNumber']
            self.ipay_id = login['ipayId']
            self.token_id = login['tokenId']
            info = self.get_entities_and_accounts()
            self.bsb = info['accounts'][0]['bsb']
            self.account_type = info['accounts'][0]['type']
            self.currency_code = info['accounts'][0]['currencyCode']
            self.save_data()
            return {
                'success': True,
                'message': 'success',
                'data': login
            }
        else:
            return {
                'success': False,
                'message': login['message'],
                'data': login
            }
    def get_balance(self,account_number):
        arr = self.get_entities_and_accounts()
        if arr['accounts']:
            amount = 0
            for v in arr['accounts']:
                if v['number'] == account_number:
                    amount = v['accountState']['availableBalance']
                    break
            return {'status': 1, 'amount': amount}
        else:
            return {'status': 0, 'data': arr}
    def get_entities_and_accounts(self):
        self.request_id = self.generate_request_id()
        params = {
            'lang': self.lang,
            'requestId': self.request_id
        }
        headers = self.header_null()
        body = self.make_body_request_json(params)
        response = requests.post(self.url['getEntitiesAndAccounts'], headers=headers, data=body, timeout=self.timeout)
        return response.json()
    def get_transaction(self, limit,start_date, end_date):
        self.request_id = self.generate_request_id()
        params = {
        'accountNumber': self.account_number,
        'endDate': end_date,
        'lang': 'vi',
        'maxResult': str(limit),
        'pageNumber': 0,
        'requestId': self.request_id,
        'searchFromAmt': '',
        'searchKey': '',
        'searchToAmt': '',
        'startDate': start_date,
        'tranType': ''
    }
        headers = self.header_null()
        body = self.make_body_request_json(params)
        response = requests.post(self.url['getHistTransactions'], headers=headers, data=body, timeout=self.timeout)
        return response.json()

    # Add other methods following the same pattern
    def build_query_string(self,params):
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return query_string
    def make_body_request_json(self, params):
        if self.session_id:
            params['sessionId'] = self.session_id
        return self.encrypt_data(params)
    def encrypt_data(self, data):
        url = "https://encrypt.pay2world.org/api.php?act=encrypt_viettin"

        payload = json.dumps(data)
        headers = {
        'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)

    def bypass_captcha(self,svg):
        model = {
            "MCLCLCLCLCLCCLCLCLCLCLCLCCLCLCLCLCCLCLCLCLCCZMCCLCLCCLCLCCLCLCCLCZ": 0,
            "MLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLZ": 1,
            "MLLLLLLLLLLLLCLCLCCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLLLLLZ": 2,
            "MCLCCLCLCCLCLCLLLLLLLLLLLCCCCCLLLLLLLLLLLLCCCCCCCCLLLLLCCCLCCLCCLCLCCZ": 3,
            "MLLLLLLLLLLLLLLLLLCLCLCCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLZMLLLLLLLLLLLLLLLZMLLLZ": 4,
            "MCLCLCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLCCLLLLLLLCLCLCZ": 5,
            "MCLCLCLCLCCCLCLCLCLCLCLCLCLCLCLCLCLCLCLCLCLCCLCLCZMLCCCCLCLCCLCZ": 6,
            "MLCLCCLCLCLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLCZ": 7,
            "MCLCLCLCCLCCLCLCLCLCCLCLCLCLCCLCCLCLCLCCLCLCCLCLCZMLCLCCCCLCZMLCCLCLCCCCLCZ": 8,
            "MLCLCLCLCLCLCCLCLCLCLCCLCLCLCLCCCCCLCLCLCLCLCLCLCLCZMLCCCCCLCLCCCCLCZ": 9
        }
        chars = {}
        matches = re.findall(r'<path fill="(.*?)" d="(.*?)"/>', svg)
        if len(matches) != 6:
            return len(matches)
        
        paths = [match[1] for match in matches]
        for path in paths:
            p = re.search(r"M([0-9]+)", path)
            if p:
                pattern = re.sub(r"[0-9 \.]", "", path)
                chars[int(p.group(1))] = model[pattern]
        
        chars = dict(sorted(chars.items()))
        return "".join(str(chars[key]) for key in chars)

    def generate_request_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)) + '|' + str(int(datetime.now().timestamp()))

    def header_null(self):
        headers = {
            "Accept-Encoding": "gzip",
            "Accept-Language": "vi-VN",
            "Accept": "application/json",
            "Cache-Control": "no-store, no-cache",
            "User-Agent": "okhttp/3.11.0"
        }
        if self.session_id:
            headers["sessionId"] = self.session_id
        return headers