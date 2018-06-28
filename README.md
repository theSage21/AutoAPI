AutoAPI
=======

A server that is able to automatically add apis to itself via HTTP requests.


```python
import requests

host = 'http://localhost:8800'

requests.post(host+'/api/register', json={"app": "powerful",
                                          "new_api": "/power/2",
                                          "code": "return {'answer': bottle.request.json.get('number') ** 2}"})


# The api is now registered You can use it instantly

r = requests.post(host+'/powerful/power/2', json={"number": 5})
assert r.json()['answer'] == 25

# One can dynamically add code to the system with this setup.
```
