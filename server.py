api = []
import bottle
import yaml
import os
from bottlecors import wide_open_cors, abort
wsgi = bottle.Bottle()
wsgi = wide_open_cors(wsgi)

__config_path = 'apps.yml'


def recycle():
    if os.path.exists(__config_path):
        with open(__config_path, 'r') as fl:
            __config = yaml.load(fl)
    else:
        __config = {}

    # --------create apps
    [os.system(i) for i in ['rm -rf apps',
                            'mkdir apps',
                            'touch apps/__init__.py']]

    for app, paths in __config.items():
        appname = f'apps/{app}.py'
        string = 'import bottle\n'
        namelist = []
        for uri, code in paths.items():
            fname = uri.strip('/').replace('/', '_')
            namelist.append(fname)
            string += f'\ndef {fname}():\n'
            for line in code.split('\n'):
                string += f'    {line}\n'
        string += '\napi = ['
        for name in namelist:
            string += name + ', '
        string = string.rstrip(',') + ']'
        with open(appname, 'w') as fl:
            fl.write(string)

    with open('server.py', 'r') as fl:
        this_file = fl.read()
        pre, post = this_file.split('\n', 1)
        for app in __config:
            if f'# ==== imports {app}' not in post:
                pre += f'\n\n# ==== imports {app}\n'
                pre += f'try:\n'
                pre += f'    from apps.{app} import api as {app}_api\n'
                pre += f'    api += [("{app}", a) for a in {app}_api]\n'
                pre += f'except Exception as e:\n'
                pre += f'    print("{app} import had error: {e}")\n'
        final_this_file = '\n'.join([pre.strip(), '\n', post.strip()])
        if this_file != final_this_file:  # Avoid infinite recursion
            with open('server.py', 'w') as fl2:
                fl2.write(final_this_file)
    return __config


__config = recycle()

def __save_config():
    with open(__config_path, 'w') as fl:
        yaml.dump(__config, fl)


@wsgi.post('/api/register')
def register_a_new_api():
    jsn = bottle.request.json
    app = jsn.get('app')
    new_api = jsn.get('new_api')
    code = jsn.get('code')
    if app is None:
        abort(404, 'no such app')
    if app not in __config:
        __config[app] = {}
    __config[app][new_api] = code
    __save_config()
    recycle()
    return ''


for app, fn in api:
    url = fn.__name__.replace('_', '/')
    url = f'/{app}/{url}'
    print(url)
    wsgi.post(url)(fn)


if __name__ == '__main__':
    wsgi.run(port=8800, host='127.0.0.1', reloader=True)
