import requests
import json
import time
import urllib


class YouZanClient(object):

    access_token_url = "https://open.koudaitong.com/oauth/token"
    resource_url = "https://open.koudaitong.com/api/oauthentry"
    authorize_url = "https://open.koudaitong.com/oauth/authorize"
    expires = 0
    _access_token = None
    state = 'teststate'

    def __init__(self, client_id, client_secret, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorize_url(self, params={}):
        if 'redirect_uri' in params:
            self.redirect_uri = params['redirect_uri']
        elif self.redirect_uri is not None:
            params['redirect_uri'] = self.redirect_uri
        else:
            return APIError('9911', 'redirect uri not given')
        params.update({'client_id': self.client_id,
                       'response_type': 'code',
                       'state': params.get('state', self.state,),
                       })
        url_args = '&'.join('{}={}'.format(key, urllib.quote(val)) for key, val in params.iteritems())
        auth_url = '{}?{}'.format(self.authorize_url, url_args)
        return auth_url

    @property
    def access_token(self):
        return self._access_token

    def set_access_token(self, token, left_time=604800):
        self._access_token = token
        self.expires = int(time.time()) + left_time

    @property
    def redirect_url(self):
        return self.redirect_uri

    def set_redirect_url(self, url):
        self.redirect_uri = url

    @property
    def is_valid(self):
        return self._access_token is not None and self.expires > int(time.time())

    def get_access_token(self, code):
        headers = {'Content-type': 'application/json'}
        data = {'code': code,
                'grant_type': "authorization_code",
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri}
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(self.access_token_url, data=data, headers=headers, verify=False)
        content, error = self._process_response(rsp)
        self.expires = int(time.time()) + content['expires_in']
        self.set_access_token(content['access_token'])
        return content, error

    def refresh_token(self, refresh_token, scope=None):
        headers = {'Content-type': 'application/json'}
        data = {'refresh_token': refresh_token,
                'grant_type': "refresh_token",
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                }
        if scope is not None:
            data.update({'scope': scope})
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(self.access_token_url, data=data, headers=headers, verify=False)
        content, error = self._process_response(rsp)
        self.expires = int(time.time()) + content['expires_in']
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
            return None, APIError(content['error'], content['error_description'])
        if 'error_response' in content:
            return None, APIError(content['error_response']['code'],
                                  content['error_response']['msg'])
        return content, None

    def get_resource(self, method, params={}):
        params['access_token'] = self._access_token
        params['method'] = method
        rsp = requests.get(self.resource_url, params=params, verify=False)
        return self._process_response(rsp)

    def post_resource(self, method, data={}):
        headers = {'Content-type': 'application/json'}
        url_args = 'method={}&access_token={}'.format(method, self._access_token)
        post_url = '{}?{}'.format(self.resource_url, url_args)
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(post_url, data=data, headers=headers, verify=False)
        return self._process_response(rsp)


class APIError(object):

    def __init__(self, code, description):
        self.code = code
        self.description = description
