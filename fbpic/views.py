from django.conf import settings 
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_facebook.decorators import facebook_required_lazy, facebook_required
from django.views.decorators.csrf import csrf_protect
from django_facebook.utils import next_redirect
from django.contrib import messages
from batcam.models import BatCamPicture, MyCustomProfile
import os
import shutil

def home(request):
    
    if request.user.is_authenticated():
        # user is logged in
        template_name = "success.html"
    else:
        template_name = "index.html"
        

    # return HttpResponse()
    context = RequestContext(request)
    return render_to_response(template_name,context)

def next(request):

    context = RequestContext(request)
    return render_to_response("success.html",context)

@csrf_protect
def tagger(request):

    context = RequestContext(request)

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    incoming_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","incoming")
    temp_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","temp")
    outgoing_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","temp")

    message = "first time"
    #if tagging has happened on this call
    if request.method == "POST":

        filename = request.POST.get('filename')
        all_user_ids = request.POST.get('all_user_ids')
        #What happens if I skip this step altogether and move it to outgoing directly in step 1 ???
        if all_user_ids == "":
            #No Tags
            message = "no tags"
        else:
            for user_id in all_user_ids.split(","):
                message = user_id.strip()

        #shutil.move(os.path.join(temp_dir_path,filename), outgoing_dir_path)


    filename = os.listdir(incoming_dir_path)[0] #add if not blank condition here or only file is .gitignore
    
    # move directories
    # shutil.move(os.path.join(incoming_dir_path,filename), temp_dir_path)

    context['filename'] = filename
    context['zone'] = "batcam"
    context['message'] = message

    return render_to_response("tagger.html",context)

def postPic(request):
    context = RequestContext(request)
    return render_to_response("success.html",context)

@facebook_required(scope='publish_actions')
@csrf_protect
def postMsg(request):
    '''
    Simple example on how to do open graph postings
    '''
    message = request.POST.get('message')
    if message:
        fb = get_persistent_graph(request)
        entity_url = 'http://www.fashiolista.com/item/2081202/'
        fb.set('me/fashiolista:love', item=entity_url, message=message)
        messages.info(request,
                      'Frictionless sharing to open graph beta action '
                      'fashiolista:love with item_url %s, this url contains '
                      'open graph data which Facebook scrapes' % entity_url)

@facebook_required(scope='publish_actions')
@csrf_protect
def wall_post(request):
    user = request.user
    graph = user.get_offline_graph()
    message = request.GET.get('message')
    picture = request.GET.get('picture')
    if message:
        graph.set('me/feed', link=picture, picture=picture, message=message)
        messages.info(request, 'Posted the message to your wall')
        return next_redirect(request)
    return HttpResponse("")