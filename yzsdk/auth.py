import datetime
import hashlib
import pytz

timezone = pytz.timezone('Asia/Shanghai')


class Auth:
    def __init__(self):
        pass

    def build_params(self, data):
        raise NotImplementedError

    def build_url(self):
        raise NotImplementedError


class Sign(Auth):
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def build_params(self, data):
        timestamp = datetime.datetime.now(
            timezone).strftime('%Y-%m-%d %H:%M:%S')
        post_data = {
            'app_id': self.app_id,
            'app_secret': self.app_secret,
            'timestamp': timestamp,
            'format': 'json',
            'sign_method': 'md5',
        }
        post_data = dict(post_data.items() + data.items())
        sorted_param_map = sorted(post_data.items(), key=lambda d: d[0])
        plain_text = self.app_secret
        for item in sorted_param_map:
            plain_text += (unicode(item[0]) + unicode(item[1]))
        plain_text += self.app_secret
        md5 = hashlib.md5(plain_text.encode("utf8")).hexdigest()
        post_data['sign'] = md5
        return post_data

    def build_url(self):
        return '/entry'


class Token(Auth):
    def __init__(self, token):
        self.token = token

    def build_url(self):
        return '/oauthentry'

    def build_params(self, data):
        data['access_token'] = self.token
        return data
