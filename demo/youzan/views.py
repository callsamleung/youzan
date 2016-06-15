from django.http import HttpResponse
from yzsdk.sdk import YouZanClient
from django.shortcuts import redirect
# Create your views here.

client = YouZanClient('ee709b850e953e912b', '10bbc0de502b27a4cba5df65d33e2d20',
                      'http://youzan.tunnel.phpor.me/youzan/')

def home(request):
    data = {'state': 'just for test'}
    url = client.get_authorize_url(data)
    return redirect(url)

def callback(request):
    code = request.GET.get('code')
    access_token, error = client.get_access_token(code)
    print access_token
    res = client.get_resource("kdt.itemcategories.tag.add", {'name': '8cvxc'})
    return HttpResponse(res)
