from django.contrib.auth                import authenticate, login, logout
from django.views.generic               import View
from django.http                        import HttpResponseRedirect
from django.shortcuts                   import render_to_response
from django.template                    import RequestContext

# this is linked to http://r2lab.inria.fr/login
# which is invoked from login_widget.html
# together with username/password in the POST data

class Login(View):

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # pass request within the token, so manifold session key can be attached to the request session.
        token = {'username': username, 'password': password, 'request': request}

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
            env['login_message'] = "Your username and/or password is incorrect"
        elif not user.is_active:
            env['login_message'] = "This user is inactive"
        # r2lab_context is expected to have been attached to the session by mfbackend
        elif 'r2lab_context' not in request.session:
            logger.error("Internal error - cannot retrieve r2lab_context")
            env['login_message'] = "Cannot log you in - please get in touch with admin"
            redirect_url = "/oops.md"
        else:
            logger.debug("login for user={}".format(user))
            login(request, user)
            env['login_message'] = "Logged in as user {}".format(user)
            env['r2lab_context'] = request.session['r2lab_context']
            redirect_url = "/status.md#livemap"

        return HttpResponseRedirect(redirect_url)

    def http_method_not_allowed(request):
        return HttpResponseRedirect("/oops.md")
        
