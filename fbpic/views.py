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
from django_facebook.models import FacebookCustomUser
from batcam.models import BatCamPicture, MyCustomProfile
from open_facebook.api import OpenFacebook
from django.db.models import Max

import os
import shutil

def home(request, name):
    
    # Calculates the maximum out of the already-retrieved objects
    debu = ""
    batcam = False
    trampoline = False
    untameable = False

    if request.user.is_authenticated():
        template_name = "success.html"
        if name=="batcam":
            batcam = True
            if not request.user.mycustomprofile.batcam_id:
                args = MyCustomProfile.objects.all()
                request.user.mycustomprofile.batcam_id = args.aggregate(Max('batcam_id'))['batcam_id__max'] + 1
                request.user.mycustomprofile.save()

        elif name=="untameable":
            untameable = True
            if not request.user.mycustomprofile.untameable_id:
                args = MyCustomProfile.objects.all()
                request.user.mycustomprofile.untameable_id = args.aggregate(Max('untameable_id'))['untameable_id__max'] + 1
                request.user.mycustomprofile.save()

        elif name=="trampoline":
            trampoline = True
            if not request.user.mycustomprofile.trampoline_id:
                args = MyCustomProfile.objects.all()
                request.user.mycustomprofile.trampoline_id = args.aggregate(Max('trampoline_id'))['trampoline_id__max'] + 1
                request.user.mycustomprofile.save()
        # user is logged in
    else:
        template_name = "index.html"
    

    # return HttpResponse()
    context = RequestContext(request, {'debu':debu,'batcam':batcam,'untameable':untameable,'trampoline':trampoline})
    return render_to_response(template_name,context)

def next(request):

    context = RequestContext(request,{'debu':request.POST.get('name')})

    return render_to_response("success.html",context)

@csrf_protect
def tagger(request):

    context = RequestContext(request)

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    incoming_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","incoming")
    temp_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","temp")
    outgoing_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","outgoing")

    message = "new session"
    #if tagging has happened on this call
    if request.method == "POST":

        filename = request.POST.get('filename')
        all_user_ids = request.POST.get('all_user_ids')
        #What happens if I skip this step altogether and move it to outgoing directly in step 1 ???
        if all_user_ids == "":
            #No Tags
            message = "no tags"
        else:
            message = ""
            shutil.move(os.path.join(temp_dir_path,filename), outgoing_dir_path)
            for user_id in all_user_ids.split(","):
                user_id = user_id.strip()
                tagged_user = FacebookCustomUser.objects.get(pk=user_id)
                facebook = OpenFacebook(tagged_user.access_token)
                facebook.set('me/feed', message='Check out my Untameable Picture',
                       picture="http://batcam.bacardiindia.in/static/fbpic/images/batcam/outgoing/"+filename, url='http://batcam.bacardiindia.in')               
                message = message + " and " + tagged_user.first_name
            

    if len(os.listdir(incoming_dir_path)) == 0:
        message = message + "No More Pictures to tag"
    else:
        filename = os.listdir(incoming_dir_path)[0] #add if not blank condition here or only file is .gitignore
        # move directories
        shutil.move(os.path.join(incoming_dir_path,filename), temp_dir_path)
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