from django.conf import settings 
from django.http import HttpResponse, StreamingHttpResponse
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
from batcam.models import BatCamPictureTag, MyCustomProfile
from open_facebook.api import OpenFacebook
from django.db.models import Max
from django.db.models import F
import pickle
import random
import httplib, urllib, urllib2
import os
import shutil

def home(request, zone):
    
    # Calculates the maximum out of the already-retrieved objects
    batcam = False
    trampoline = False
    untameable = False
    debu =""
    if request.user.is_authenticated():
        template_name = "success.html"
        if zone=="batcam1" or zone=="batcam2":
            batcam = True
            if not request.user.mycustomprofile.batcam_id:
                with open(str(zone)+"_ids.p","r") as file_handle:
                    list_of_ids = pickle.load(file_handle)

                current_id = list_of_ids.pop(0)

                with open(str(zone)+"_ids.p","w") as file_handle:
                    pickle.dump(list_of_ids,file_handle)
                
                request.user.mycustomprofile.batcam_id = current_id
                request.user.mycustomprofile.save()
        elif zone == "untameable" or zone == "trampoline":
            current_id = 0
            if zone=="untameable":
                untameable = True
                
                if not request.user.mycustomprofile.untameable_id:
                    args = MyCustomProfile.objects.all()
                    current_id = request.user.mycustomprofile.untameable_id = args.aggregate(Max('untameable_id'))['untameable_id__max'] + 1
                

            elif zone=="trampoline":
                trampoline = True

                if not request.user.mycustomprofile.trampoline_id:
                    args = MyCustomProfile.objects.all()
                    current_id = request.user.mycustomprofile.trampoline_id = args.aggregate(Max('trampoline_id'))['trampoline_id__max'] + 1

            request.user.mycustomprofile.save()

            with open(str(zone)+"_ids.p","r") as file_handle:
                list_of_ids = pickle.load(file_handle)

            if len(list_of_ids) > 10:
                list_of_ids.pop(0)

            if(list_of_ids[-1]!=current_id):
                list_of_ids.append(current_id)
            
            with open(str(zone)+"_ids.p","w") as file_handle:
                pickle.dump(list_of_ids,file_handle)

        # user is logged in
        elif zone=="none":
            batcam = False
            untameable = False
            trampoline = False
            # Fill this up later

    else:
        template_name = "index.html"
    

    # return HttpResponse()
    context = RequestContext(request, {'debu':debu,'zone':zone, 'batcam':batcam,'untameable':untameable,'trampoline':trampoline})
    return render_to_response(template_name,context)

def next(request):

    context = RequestContext(request,{'debu':request.POST.get('name')})

    return render_to_response("success.html",context)

@csrf_protect
def tagger(request, zone):

    context = RequestContext(request)

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    incoming_dir_path = os.path.join(BASE_DIR, "static","fbpic","images",zone,"incoming")
    temp_dir_path = os.path.join(BASE_DIR, "static","fbpic","images",zone,"temp")
    outgoing_dir_path = os.path.join(BASE_DIR, "static","fbpic","images",zone,"outgoing")
    discared_dir_path = os.path.join(BASE_DIR, "static","fbpic","images",zone,"discard")

    message = zone + "new session"
    #if tagging has happened on this call
    if request.method == "POST":

        filename = request.POST.get('filename')
        all_user_ids = request.POST.get('all_user_ids')
        #What happens if I skip this step altogether and move it to outgoing directly in step 1 ???
        if all_user_ids == "":
            #No Tags
            message = "no tags"
            shutil.move(os.path.join(temp_dir_path,filename), discard_dir_path)
        else:
            message = ""
            shutil.move(os.path.join(temp_dir_path,filename), outgoing_dir_path)
            for user_id in all_user_ids.split(","):
                user_id = int(user_id.strip())
                if zone == "batcam":
                    tagged_user = MyCustomProfile.objects.get(batcam_id__exact=user_id)
                    # Increase tagged count
                    tagged_user.tagged_count = tagged_user.tagged_count + 1
                    tagged_user.save() 

                    # Make entry in tagged table
                    picture_tag = BatCamPictureTag.objects.create(
                    complete_path = os.path.join(outgoing_dir_path,filename),
                    filename = filename,
                    batcam_id = user_id,
                    zone = "B",
                    all_user_ids = all_user_ids
                    )
                    picture_tag.save()

                    
                elif zone == "untameable":
                    tagged_user = MyCustomProfile.objects.get(untameable_id__exact=user_id)
                    facebook = OpenFacebook(tagged_user.user.access_token, version = 'v2.1')
                    #Message can be randomized? Is it worth the risk?
                    url_var="http://batcam.bacardiindia.in"+"/static/fbpic/images/"+zone+"/outgoing/"+filename
                    message = url_var
                    facebook_return = facebook.set('me/photos', message="I'm at Bacardi Untameable Zone",
                       url=url_var, place='206635469415060')
                    
                    picture_tag = BatCamPictureTag.objects.create(
                    complete_path = os.path.join(outgoing_dir_path,filename),
                    filename = filename,
                    batcam_id = user_id,
                    zone = "U",
                    all_user_ids = all_user_ids,
                    posted_to_facebook =True,
                    facebook_post_id = facebook_return["id"],
                    )
                    picture_tag.save()

                elif zone =="trampoline":
                    tagged_user = MyCustomProfile.objects.get(trampoline_id__exact=user_id)
                    #tagged_user = FacebookCustomUser.objects.get(pk=user_id)

                    facebook = OpenFacebook(tagged_user.user.access_token, version = 'v2.1')
                    #Message can be randomized? Is it worth the risk?
                    facebook_return = facebook.set('me/photos', message='',
                       url="http://batcam.bacardiindia.in"+"/static/fbpic/images/"+zone+"/outgoing/"+filename, place='206635469415060')

                    picture_tag = BatCamPictureTag.objects.create(
                    complete_path = os.path.join(outgoing_dir_path,filename),
                    filename = filename,
                    batcam_id = user_id,
                    zone = "T",
                    all_user_ids = all_user_ids,
                    posted_to_facebook =True,
                    facebook_post_id = facebook_return["id"],
                    )
                    picture_tag.save()

                message = tagged_user.user.first_name + ", "
            

    if len(os.listdir(incoming_dir_path)) == 0:
        message = message + "No More Pictures to tag"
    else:
        filename = os.listdir(incoming_dir_path)[0] #add if not blank condition here or only file is .gitignore
        # move directories
        shutil.move(os.path.join(incoming_dir_path,filename), temp_dir_path)
        context['filename'] = filename
    
    context['message'] = message
    context['zone'] = zone
    return render_to_response("tagger.html",context)

@csrf_protect
def lastuser(request, zone):
    list_of_users = []
    list_of_ids = []
    with open(str(zone)+"_ids.p","r+") as file_handle:
        list_of_ids = pickle.load(file_handle)
        if zone == "untameable":
            for each_id in list_of_ids:
                list_of_users.append(MyCustomProfile.objects.get(untameable_id__exact=each_id))
        if zone == "trampoline":
            for each_id in list_of_ids:
                list_of_users.append(MyCustomProfile.objects.get(trampoline_id__exact=each_id))

    context = RequestContext(request, {'zone':zone, 'list_of_users':list_of_users,'list_of_ids':list_of_ids})
    return render_to_response("lastuser.html",context)


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

@csrf_protect
def poster(request):
    message = ""

    if request.method == "POST":
        keepers = request.POST.getlist('keep')
        ids = request.POST.getlist('pic-id')
        filenames = request.POST.getlist('pic-filename')
        heroes = request.POST.getlist('hero')
        batcam_id = request.POST.get('batcam_id')
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        outgoing_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","batcam","outgoing")


        #for zone=B, batcam-id and photo match, all must be marked as discard
        BatCamPictureTag.objects.filter(batcam_id__exact=batcam_id,zone__exact="B",id__in=ids).update(keeper="N")
        total_count = len(ids)

        #for zone=B, batcam-id and photo match, all keepers must be marked "Y" in keeper
        BatCamPictureTag.objects.filter(batcam_id__exact=batcam_id,zone__exact="B",ids__in=keepers).update(keeper="Y")
        keeping_count = len(keepers)

        #for zone=B, batcam-id and photo match, first hero must be marked "Y" in hero & keeper
        BatCamPictureTag.objects.filter(batcam_id__exact=batcam_id,zone__exact="B",ids__in=heroes).update(hero="Y")
        BatCamPictureTag.objects.filter(batcam_id__exact=batcam_id,zone__exact="B",ids__in=heroes).update(keeper="Y")
        hero_count = len(heroes)


        #if posted count=0, post one now, and update post count
        this_user = MyCustomProfile.objects.filter(batcam_id__exact=batcam_id)
        if (this_user.posted_count == 0 and keeping_count != 0):
                    photo_id = keepers[0]
                    photo_to_upload = BatCamPictureTag.objects.get(pk=photo_id)

                    facebook = OpenFacebook(this_user.user.access_token, version = 'v2.1')
                    #Message can be randomized? Is it worth the risk?
                    facebook_return = facebook.set('me/photos', message='',
                       url="http://batcam.bacardiindia.in"+"/static/fbpic/images/batcam/outgoing/"+photo_to_upload.filename, place='206635469415060')
                    photo_to_upload.posted_to_facebook = True
                    photo_to_upload.facebook_post_id = facebook_return
                    photo_to_upload.save()
                    this_user.posted_count = F('posted_count') + 1

        #Update all other counts
        discard_count = total_count - keeping_count
        this_user.discard_count = F('discard_count') + discard_count
        this_user.keep_count = F('keep_count') + keep_count
        this_user.hero_count = F('hero_count') + hero_count
        this_user.save()



    dusers = MyCustomProfile.objects.filter(batcam_id__gte=1).order_by('posted_count','-tagged_count','keep_count','hero_count')[:1]
    duser = dusers[0]
    photos = BatCamPictureTag.objects.filter(zone__exact="B",batcam_id__exact=duser.batcam_id).exclude(keeper__exact="N")

    context = RequestContext(request,{'postee':duser,'photos':photos,'message':message})
    return render_to_response("poster.html",context)

def uploader(request):
    tramp_id=118
    tagged_user = MyCustomProfile.objects.get(untameable_id=tramp_id)
    
    url_var = "http://batcam.bacardiindia.com/static/fbpic/images/untameable/outgoing/"+str(tramp_id)+".jpg"
    """
    facebook = OpenFacebook(tagged_user.user.access_token)
    facebook_return = facebook.set('me/photos', message="",
                       url=url_var, place='374502716046163')
    """
    data = urllib.urlencode({'message': '',
    'place': '374502716046163',
    'url': url_var})
    h = httplib.HTTPConnection('graph.facebook.com')
    headers = {'access_token': tagged_user.user.access_token,
                'method': 'post'}
    h.request('POST', '/me/photos', data, headers)
    r = h.getresponse()
    

    """
    picture_tag = BatCamPictureTag.objects.create(
                    complete_path = os.path.join(outgoing_dir_path,filename),
                    filename = filename,
                    batcam_id = user_id,
                    zone = "T",
                    all_user_ids = all_user_ids,
                    posted_to_facebook =True,
                    facebook_post_id = facebook_return["id"],
                    )
    picture_tag.save()
    """
    context = RequestContext(request,{"facebook_response":r.read()})
    return render_to_response("uploader.html",context)

def untameable_poster(request):
    
    context = RequestContext(request,{"facebook_response":"Done"})
    #return render_to_response("uploader.html",context)
    list_of_ids_1 = [2599,2598,2549,2482,2096,2600,2149,2150,2193,2508,2148,2540,2548,2133,2134,2135,2505,2541,2074,2075,2076,2099,2536,2547,2463,2464,2466,2465,2597,2596,2595,2594,2593,2592,2591,2147,2116,2098,2097,2170,2169,2125,2502,2503,2504,2197,2501,2186,2187,2100,2118,2121,2120,2119,2558,2559,2560,2561,2122,2571,2570,2569,2568,2567,2566,2565,2564,2497,2117,2562,2079,2081,2500,2182,2181,2180,2167,2525,2524,2530,2529,2528,2527,2526,2531,2532,2162,2163,2164,2138,2137,2136,2550,2195,2194,2554,2553,2552,2551,2142,2143,2144,2575,2574,2477,2478,2476,2517,2518,2519,2520,2521,2522,2523,2481,2480,2095,2093,2094,2092,2091,2090,2089,2141,2139,2140,2171,2123,2556,2506,2161,2160,2159,2158,2498,2563,2579,2580,2543,2157,2557,2499,2173,2555,2124,2172,2174,2175,2176,2177,2178,2078,2534,2107,2108,2106,2109,2110,2111,2112,2113,2533]
    list_of_ids_2 = [4412,4422,4112,4102,4360,4340,4019,4300,4320,4009,4409,4399,4389,4252,4262,4282,4342,4292,4272,4432,4018,4028,4038,4048,4109,4299,4309,4319,4041,4051,4061,4071,4081,4091,4064,4054,4044,4357,4347,4337,4307,4327,4317,4297,4087,4097,4077,4067,4057,4047,4287,4277,4267,4247,4034,4024,4014,4084,4094,4394,4004,4404,4377,4387,4397,4367,4005,4015,4025,4035,4046,4037,4385,4395,4257,4417,4427,4437,4117,4107,4242,4322,4312,4302,4278,4288,4027,4017,4007,4407,4052,4042,4032,4082,4092,4022,4012,4002,4402,4392,4382,4372,4362,4352,4074,4108,4072,4062,4375,4085,4265,4285,4295,4305,4325,4315,4308,4438,4118,4418,4428,4248,4258,4318,4268,4338,4058,4328,4299,4413,4423,4433,4113,4103,4266,4286,4256,4246,4416,4436,4426,4116,4106,4093,4031,4001,4021,4011,4301,4311,4321,4331,4293,4283,4343,4273,4263,4253,4243,4083]

    with open("batcam1_ids.p","w") as file_handle:
        pickle.dump(list_of_ids_1,file_handle)
    
    with open("batcam2_ids.p","w") as file_handle:
        pickle.dump(list_of_ids_2,file_handle)

    return render_to_response("uploader.html",context)
    #return StreamingHttpResponse(batcam_iterator())

def batcam_iterator():
    batcam_copies = [ "Just got caught by the eye in the sky! Here's a glimpse from the drone #BatCam",
    "This is awesome! At #BacardiNH7Weekender, Pune got snapped by the drone #BatCam. ",
    "The drone caught me! Here's my picture by the #BatCam",
    "The Drone just snapped me at #BacardiNH7Weekender, Pune. #BatCam Check it out!",
    "Here's me getting snapped by the drone at #BacardiNH7Weekender, Pune. Thank you #BatCam!"]
    all_tags = BatCamPictureTag.objects.all()
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    #incoming_dir_path = os.path.join(BASE_DIR, "static","fbpic","images",zone,"incoming")
    #list_of_filenames = []
    duser = "a"
    a=[]

    with open("fb_dump_log.p","a") as out:
        for single_tag in all_tags:
            current_filename = single_tag.filename
            current_id = single_tag.batcam_id
            try:
                current_user = MyCustomProfile.objects.get(batcam_id__exact=current_id)
            except:
                current_user = MyCustomProfile.objects.get(batcam_day2_id__exact=current_id)

            duser = current_user.user
            fb = duser.get_offline_graph()

            upload_directoy = "static/fbpic/images/batcam/outgoing/"
            zone = "T" ##can be B, U or T

            picture="http://batcam.bacardiindia.in/"+upload_directory+str(current_filename)
            b= dict()
            b['batcam_id'] = current_id
            b['name'] = duser.first_name+" "+duser.last_name
            b['picture'] = picture

            picture_tag = BatCamPictureTag.objects.create(
                    complete_path = os.path.join(outgoing_dir_path,filename),
                    filename = filename,
                    batcam_id = user_id,
                    zone = "T",
                    all_user_ids = all_user_ids,
                    posted_to_facebook =True,
                    facebook_post_id = facebook_return["id"],
                    )
            picture_tag.save()

            try:
                dummy="dumb"
                #b['response'] = fb.set('me/photos', url=picture, message=batcam_copies[random.randint(0, 4)],place="374502716046163")
            except Exception, e:
                b['response'] = str(e)
                b['error']="error generated"
            except:
                b['error']="error generated"
            pickle.dump(b,out)
            yield pickle.dumps(b) + "\r\n<br />"
            a.append(b)

@csrf_protect
def reRegister(request,batcam_original_id):
    batcam_user = MyCustomProfile.objects.get(batcam_id__exact=batcam_original_id)
    context = RequestContext(request,{"facebook_response":str(batcam_user.id)+" "+str(batcam_user.user.first_name)+" "+str(batcam_user.user.last_name)})
    return render_to_response("uploader.html",context)
