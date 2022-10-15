# Taken from https://github.com/m7v8/django-basic-authentication-decorator/blob/master/django_basic_auth.py
# BSD license

import base64

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login

BASIC_AUTH_REALM = "YcEtcwivHhC9LZYoTzzq"


def logged_in(request):
    if hasattr(request, "user") and request.user.is_authenticated:
        return request.user

    return None


def view_or_basicauth(request, *_, **__):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """

    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':', 1)

                if (user := logged_in(request)) is not None or \
                        (user := authenticate(request, username=uname, password=passwd)) is not None:
                    login(request, user)
                    request.user = user
                    return HttpResponseRedirect("/overview")

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = f'Basic realm="{BASIC_AUTH_REALM}"'
    return response


def logged_in_or_basicauth():
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.
    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.
    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.
    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.
    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)
    Use is simple:
    @logged_in_or_basicauth()
    def your_view:
        ...
    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(_):
        def wrapper(__, *args, **kwargs):
            return view_or_basicauth(
                    args[0],
                    *args,
                    **kwargs)
        return wrapper
    return view_decorator

