# youzan_sdk_python
有赞的python接口
## 这是有赞的sdk接口，可以通过该接口获取token，获取数据和提交数据
设置client
```
client = YouZanClient('ee709b850e953e912b', '10bbc0de502b27a4cba5df65d33e2d20',
                      'http://youzan.tunnel.phpor.me/youzan/')
```

获取token
```
client.get_access_token(code)
code 是回调函数中获得的字符串
```

获取数据
```
client.get_resource(way, **params)
```
