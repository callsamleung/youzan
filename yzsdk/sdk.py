# -*- coding: utf-8 -*-
import requests
import json
import time
import urllib
import datetime
import collections
# 关闭 https 提醒
requests.packages.urllib3.disable_warnings()


class YouZanClient(object):

    access_token_url = "https://open.youzan.com/oauth/token"
    resource_url = "https://open.youzan.com/api/oauthentry"
    authorize_url = "https://open.youzan.com/oauth/authorize"
    _access_token = None
    state = 'teststate'

    def __init__(self, client_id, client_secret, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self._access_token = None

    def get_authorize_url(self, params={}):
        if 'redirect_uri' in params:
            self.redirect_uri = params['redirect_uri']
        elif self.redirect_uri is not None:
            params['redirect_uri'] = self.redirect_uri
        else:
            return APIError('9911', 'redirect uri not given')
        params.update({
            'client_id': self.client_id,
            'response_type': 'code',
            'state': params.get(
                'state',
                self.state, ),
        })
        url_args = '&'.join('{}={}'.format(key, urllib.quote(val))
                            for key, val in params.iteritems())
        auth_url = '{}?{}'.format(self.authorize_url, url_args)
        return auth_url

    @property
    def access_token(self):
        return self._access_token

    def set_access_token(self, token, left_time=604800):
        self._access_token = token

    @property
    def redirect_url(self):
        return self.redirect_uri

    def set_redirect_url(self, url):
        self.redirect_uri = url

    @property
    def is_valid(self):
        return self._access_token is not None and self.expires > int(
            time.time())

    def get_access_token(self, code):
        headers = {'Content-type': 'application/json'}
        data = {
            'code': code,
            'grant_type': "authorization_code",
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(
            self.access_token_url, data=data, headers=headers, verify=False)
        content, error = self._process_response(rsp)
        if not error and 'access_token' in content:
            self.set_access_token(content['access_token'])
        return content, error

    def refresh_token(self, refresh_token, scope=None):
        headers = {'Content-type': 'application/json'}
        data = {
            'refresh_token': refresh_token,
            'grant_type': "refresh_token",
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        if scope is not None:
            data.update({'scope': scope})
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(
            self.access_token_url, data=data, headers=headers, verify=False)
        content, error = self._process_response(rsp)
        if not error and 'access_token' in content:
            self.set_access_token(content['access_token'])
        return content, error

    def _process_response(self, rsp):
        if rsp.status_code != 200:
            return None, APIError(rsp.status_code, "http_error")
        try:
            content = rsp.json()
        except:
            return None, APIError('9999', 'invald rsp')
        if 'error' in content:
            return None, APIError(content['error'],
                                  content['error_description'])
        if 'error_response' in content:
            return None, APIError(content['error_response']['code'],
                                  content['error_response']['msg'])
        return content, None

    def _get_valid_token(self, token):
        if token is not None:
            return token
        else:
            return self._access_token

    def get_resource(self, method, token=None, params={}):
        token = self._get_valid_token(token)
        if token is None:
            return None, APIError(
                'token miss',
                'you have to give a token by pass_in or get_access_token method'
            )
        params['access_token'] = token
        params['method'] = method
        rsp = requests.get(self.resource_url, params=params, verify=False)
        return self._process_response(rsp)

    def post_resource(self, method, token=None, data={}):
        post_token = self._get_valid_token(token)
        if token is None:
            return None, APIError(
                'token miss',
                'you have to give a token by pass_in or get_access_token method'
            )
        headers = {'Content-type': 'application/json'}
        url_args = 'method={}&access_token={}'.format(method, post_token)
        post_url = '{}?{}'.format(self.resource_url, url_args)
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(post_url, data=data, headers=headers, verify=False)
        return self._process_response(rsp)

    def get_shop_info(self, token=None):
        method = 'kdt.shop.basic.get '
        content, error = self.get_resource(method=method, token=token)
        return content, error

    def get_order_info_on_buyer_id(self, buyer_id, page, size, token=None):
        method = 'kdt.trades.sold.get'
        content, error = self.get_resource(
            method=method,
            token=token,
            params={'buyer_id': buyer_id,
                    'page_no': page,
                    'page_size': size})
        return content, error


class YouZanDevelopClient(object):
    access_token_url = "https://open.youzan.com/oauth/token"
    resource_url = "https://open.youzan.com/api/oauthentry"
    user_url = "https://uic.youzan.com/sso/open/"

    def __init__(self, client_id='', client_secret='', ua=''):
        self._ua = ua
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, token):
        self._access_token = token

    def sync_user(self, data):
        sync_url = 'https://wap.koudaitong.com/v2/buyer/kdtunion/index.json?'
        headers = {
            'Content-type': 'application/json',
            'User-Agent': "KdtUnion_" + self._ua
        }
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(sync_url, data=data, headers=headers, verify=False)
        return self._process_response(rsp)

    def init_token(self):
        sync_url = self.user_url + 'initToken'
        data = {
            "user_agent": self._ua,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        rsp = requests.post(sync_url, data=data, verify=False)
        return self._process_response(rsp)

    def login_user(self, data):
        sync_url = self.user_url + 'login'
        data.update({
            "user_agent": self._ua,
            "client_id": self._client_id,
            "client_secret": self._client_secret
        })
        rsp = requests.post(sync_url, data=data, verify=False)
        return self._process_response(rsp)

    def register_user(self, data):
        sync_url = self.user_url + 'register'
        data.update({
            "user_agent": self._ua,
            "client_id": self._client_id,
            "client_secret": self._client_secret
        })
        print data
        print sync_url
        rsp = requests.post(sync_url, data=data, verify=False)
        print rsp.content
        print rsp.url
        return self._process_response(rsp)

    def logout_user(self, data):
        sync_url = self.user_url + 'logout'
        data.update({
            "user_agent": self._ua,
            "client_id": self._client_id,
            "client_secret": self._client_secret
        })
        rsp = requests.post(sync_url, data=data, verify=False)
        return self._process_response(rsp)

    def send_message_to_youzan(self, data):
        request_url = self.resource_url + '/courier.fans.message/1.0.0/send'
        headers = {'Content-type': 'application/json'}
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(
            request_url, data=data, headers=headers, verify=False)
        return self._process_response(rsp)

    def get_token(self, user_id, scope=None):
        headers = {'Content-type': 'application/json'}
        post_data = {
            'grant_type': 'yz_union',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'ua': self._ua,
            'user_id': user_id
        }
        if scope is not None:
            post_data['scope'] = scope
        data = json.dumps(post_data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(
            self.access_token_url, data=data, headers=headers, verify=False)
        content, error = self._process_response(rsp)
        if error is None:
            self._access_token = content['accessToken']
        return content, error

    def _get_resource(self, method, data):
        params = dict()
        params['access_token'] = self._access_token
        params['method'] = method
        params.update(data)
        rsp = requests.get(self.resource_url, params=params, verify=False)
        return self._process_response(rsp)

    def _post_resource(self, method, data):
        headers = {'Content-type': 'application/json'}
        url_args = 'method={}&access_token={}'.format(method,
                                                      self._access_token)
        post_url = '{}?{}'.format(self.resource_url, url_args)
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(post_url, data=data, headers=headers, verify=False)
        return self._process_response(rsp)

    def _process_response(self, rsp):
        if rsp.status_code != 200:
            return None, APIError(rsp.status_code, "http_error")
        try:
            print rsp.json()
            content = rsp.json()
        except:
            return None, APIError('9999', 'invald rsp')
        print content
        if 'code' in content and str(content['code']) != '0':
            message = content.get('message')
            if message is None:
                message = content.get('msg')
            return None, APIError(content.get('code'), message)
        elif 'error_code' in content and content['error_code'] != '0':
            return None, APIError(
                content.get('error_code'), content.get('error_message'))
        elif 'error' in content:
            return None, APIError(
                content.get('error'), content.get('error_description'))
        elif 'error_response' in content:
            return None, APIError(content['error_response'].get('code'),
                                  content['error_response'].get('msg'))
        return content, None


class YouZanAuthClient(object):
    def __init__(self,
                 authorize,
                 request_url="https://open.youzan.com/api"):
        self.request_url = request_url
        self.api_version = '1.0.0'
        self.auth = authorize

    def invoke(self, apiname, method, data=None):
        service = apiname[0:apiname.rindex('.')]
        action = apiname[apiname.rindex('.') + 1:len(apiname)]
        if data is None:
            data = {}

        param_map = self.auth.build_params(data)
        request_url = self.request_url + self.auth.build_url()
        url = '/'.join([request_url, service, self.api_version, action])

        print url
        print method
        print param_map
        rsp = self.send_request(url, method, param_map)
        print rsp.text
        return self._process_response(rsp)

    def send_request(self, url, method, param_map):
        if method.upper() == 'GET':
            return requests.get(url=url, params=param_map, verify=False)
        elif method.upper() == 'POST':
            return requests.post(url=url, data=param_map, verify=False)

    def _process_response(self, rsp):
        if rsp.status_code != 200:
            return None, APIError(rsp.status_code, "http_error")
        try:
            ret_content = rsp.json()
            content = ret_content['response']
        except:
            return None, APIError('9999', 'invald rsp')
        if 'error_response' in ret_content:
            error = ret_content['error_response']
            error_code = error.get('code')
            error_msg = error.get('msg')
            return None, APIError(error_code, error_msg)
        if content.get('success') is False:
            if 'msg' in content:
                error_code = content.get('resultCode', '9988')
                error_msg = content.get('msg', '')
            elif 'commonError' in content:
                commonError = content['commonError']
                error_code = commonError.get('errorCode', '9988')
                error_msg = commonError.get('errorMessage', '')
            else:
                error_code = content.get('errorCode', '9987')
                error_msg = self._youzan_pay_exception_map(error_code)
            return None, APIError(error_code, error_msg)
        return content, None

    def _youzan_pay_exception_map(self, error_id):
        error = {
            "117400004": u"请求参数错误",
            "117400008": u"商户重复注册其下的用户",
            "117400009": u"父商户号的账号角色不为商户",
            "117400006": u"输入的商户号不存在",
            "117400003": u"未知异常",
            "112200100": u"处理成功",
            "112000000": u"重复支付",
            "112200001": u"处理失败",
            "112200002": u"未知异常",
            "112200003": u"系统错误",
            "112200004": u"参数错误",
            "112202005": u"用户Token错误",
            "112202006": u"三方支付工具没有返回deepLink",
            "112202007": u"三方支付工具预支付失败",
            "112202008": u"商户配置信息错误",
            "114999986": u"支付工具异常",
            "114999979": u"支付模式不存在",
        }.get(error_id, u"未知异常")
        return error


class APIError(object):
    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return u'YZError: code: %s msg: %s' % (self.code, self.description)

    def __unicode__(self):
        return u'YZError: code: %s msg: %s' % (self.code, self.description)
