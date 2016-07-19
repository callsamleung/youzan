from django.http import HttpResponse
from yzsdk.sdk import YouZanClient
from django.shortcuts import redirect
# Create your views here.

client = YouZanClient('ee709b850e9dddsfds', '10bbc0de5dfsddsfdssd',
                      'http://youzan.tunnel.phpor.me/youzan/')


def home(request):
    data = {'state': 'just for test'}
    url = client.get_authorize_url(data)
    return redirect(url)


def callback(request):
    code = request.GET.get('code')
    access_token, error = client.get_access_token(code)
    print access_token
    return HttpResponse(access_token)

def test(request):
    token = '72ae51ee38693ca98cf6c850ba8917ba'
    content, error = client.get_shop_info(token)
    print content, error
    return HttpResponse(content)
