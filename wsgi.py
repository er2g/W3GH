import os
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app as flask_app


class PrefixMiddleware:
    def __init__(self, app, prefix: str):
        self.app = app
        self.prefix = prefix.rstrip('/')

    def __call__(self, environ, start_response):
        prefix = self.prefix
        if not prefix:
            return self.app(environ, start_response)

        path = environ.get('PATH_INFO', '')
        if path.startswith(prefix + '/') or path == prefix:
            environ['SCRIPT_NAME'] = prefix
            environ['PATH_INFO'] = path[len(prefix):] or '/'
        return self.app(environ, start_response)


flask_app.config['PREFERRED_URL_SCHEME'] = 'https'

app = ProxyFix(flask_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app = PrefixMiddleware(app, prefix=os.environ.get('W3GH_PREFIX', '/spo'))
