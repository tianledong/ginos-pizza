from django.http import HttpResponseRedirect
from django.contrib import messages


def login_required_message(function):
    def warp(request, *args, **kwargs):
        if request.user.is_authenticated is True:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'please sign in to continue!')
            return HttpResponseRedirect('/signin/')
    return warp
