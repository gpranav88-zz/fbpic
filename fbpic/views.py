from django.conf import settings 
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def home(request):
    """
    A base view.
    """
    template_name = "index.html"

    # return HttpResponse()
    context = RequestContext(request)
    return render_to_response(template_name,context)

def next(request):

    context = RequestContext(request)
    return render_to_response("success.html",context)