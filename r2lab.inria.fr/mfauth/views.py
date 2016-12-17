from django.contrib.auth                import authenticate, login, logout
from django.views.generic               import View
from django.http                        import HttpResponseRedirect
from django.shortcuts                   import render_to_response
from django.template                    import RequestContext

import md.views
from r2lab.settings import logger

# this is linked to http://r2lab.inria.fr/login
# which is invoked from widget_login.html
# together with username/password in the POST data


class Login(View):

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # pass request within the token, so manifold session key can be
        # attached to the request session.
        token = {'username': username,
                 'password': password, 'request': request}

        # authentication occurs through the backend
        # our authenticate function returns either
        # . a ManifoldResult - when something has gone wrong, like e.g. backend is unreachable
        # . a django User in case of success
        # . or None if the backend could be reached but the authentication failed
        user = authenticate(token=token)

        # default redirection URL - for failures
        redirect_url = "/"

        env = {}
        if user is None:
            env['login_message'] = "incorrect username and/or password"
            return md.views.markdown_page(request, 'index', env)
        elif not user.is_active:
            env['login_message'] = "this user is inactive"
            return md.views.markdown_page(request, 'index', env)
        # r2lab_context is expected to have been attached to the session by
        # mfbackend
        elif 'r2lab_context' not in request.session:
            logger.error("Internal error - cannot retrieve r2lab_context")
            env['login_message'] = "cannot log you in - please get in touch with admin"
            return md.views.markdown_page(request, 'oops', env)
        elif 'hrn' not in request.session['r2lab_context']['mfuser']:
            env['login_message'] = "this user has no slice !"
            return md.views.markdown_page(request, 'index', env)
#        elif 'slicenames' not in request.session['r2lab_context'] or \
#                not request.session['r2lab_context']['slicenames']:
#            env['login_message'] = "this user has no slice !"
#            return md.views.markdown_page(request, 'index', env)
        else:
            logger.debug("login for user={}".format(user))
            login(request, user)
            env['login_message'] = "Logged in as user {}".format(user)
            env['r2lab_context'] = request.session['r2lab_context']
            return md.views.markdown_page(request, 'run', env)

    def http_method_not_allowed(self, request):
        env = {'login_message': 'HTTP method not allowed'}
        return md.views.markdown_page(request, 'oops', env)


class Logout(View):
    # using GET for now - should probably be POST instead some day

    def get(self, request):
        env = {}
        if 'r2lab_context' not in request.session or \
                'mfuser' not in request.session['r2lab_context']:
            env['login_message'] = 'cannot logout - not logged in'
            return md.views.markdown_page(request, 'index', env)
        logout(request)
        env['login_message'] = 'logged out'
        return md.views.markdown_page(request, 'index', env)

    def http_method_not_allowed(self, request):
        env = {'login_message': 'HTTP method not allowed'}
        return md.views.markdown_page(request, 'oops', env)
