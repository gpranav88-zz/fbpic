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
import json
import pickle
import random
import httplib, urllib, urllib2
import os
import shutil

def home(request):
    
    # Calculates the maximum out of the already-retrieved objects
    
    text = ""
    custom_profile = ""
    if request.user.is_authenticated():
        template_name = "success.html"
        try:
            custom_profile = MyCustomProfile.objects.get(user__exact=request.user.id)
        except:
            custom_profile = MyCustomProfile(user=request.user.id)
            custom_profile.save()


        if not custom_profile.newuid:
            #assign id here, kit_id
            try:
                list_of_ids = []
                with open("lumia_hand_ids.p","r+") as file_handle:
                    list_of_ids = pickle.load(file_handle)
                    current_id = list_of_ids.pop(0)
                    pickle.dump(list_of_ids,file_handle)
                    custom_profile.newuid = text = current_id

                with open("lumia_hand_ids.p","w") as file_handle:
                    pickle.dump(list_of_ids,file_handle)

            except:
                custom_profile.newuid = text = 0

            custom_profile.save()
        else:
            text = custom_profile.newuid   
    else:
        template_name = "index.html"
    

    # return HttpResponse()
    context = RequestContext(request,{'text':text})
    return render_to_response(template_name,context)

def home2(request):
    
    # This is a test pot for hoem page
    list_of_ids = [4008,4007,4006,4022,4023,4024,4025,4783,4782,4781,4780,4779,3800,3799,3798,3797,3796,3795,3794,3793,3792,3791,3259,3258,3257,3256,3675,3674,3673,3672,3671,3670,3669,3668,4005,4026,4004,4027,4028,4030,4029,4031,4003,4002,4001,4000,3999,4032,4021,4333,4334,4049,3051,3052,3053,3054,3055,3056,3057,3058,3059,3060,3061,3062,3946,3947,3950,3949,3948,3099,3100,3000,2999,2998,2997,2996,2995,2994,2888,2572,2571,2570,3080,3079,3078,3077,3076,3075,3074,3073,3072,3071,4012,4009,4020,4010,4019,4018,4017,4016,4015,4014,3780,3779,4013,4011,3778,2662,2663,2664,2665,2666,2667,2668,2669,2670,2671,2672,2673,2674,2675,2676,2677,4201,4202,4203,4204,4205,4206,4207,3098,4208,4209,4210,4211,4212,4213,4214,4215,4216,4217,4218,4048,4046,4047,4045,4044,3465,3464,3463,3462,3461,3460,3459,3458,3457,3456,3455,3454,3453,3452,3451,2661,2660,2659,2658,2657,2656,3240,3239,3238,3237,3236,3235,3204,3097,3096,3095,3094,3093,3092,3091,3090,3089,3088,3087,3086,3085,3084,3083,3082,3081,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,2713,2707,2714,2730,2706,2705,2704,2703,2702,2701,2700,2699,2696,2695,2694,2693,2712,2698,2697,2708,2709,2711,2692,2710,3991,3992,4042,4041,3993,4040,3995,4039,4038,3997,3996,4036,4332,4331,4330,4329,4328,4327,4326,4325,4324,4323,4322,4321,4320,4319,4318,4317,4316,4315,4314,4313,4312,4311,4310,4309,4308,4307,4306,3570,3569,3568,3567,3566,3565,3564,3563,3562,3561,3560,3559,3558,3557,3556,2562,2563,2564,2565,2566,2567,2568,2569,3666,4941,4940,4939,4938,4937,3665,3664,3663,3662,3661,3660,3659,3658,3657,3656,3655,3654,3653,3652,3651,3650,3649,3648,3790,3789,3788,3787,3786,3785,3784,3783,3782,3781,4410,4409,4408,4407,4406,4405,4404,4403,4402,4401,4400,4399,4398,4397,4396,4395,4394]
    
    
    with open("lumia_hand_ids.p","w") as file_handle:
        pickle.dump(list_of_ids,file_handle)

    return HttpResponse("Done")
    #context = RequestContext(request)
    #return render_to_response(template_name,context)

def next(request):

    context = RequestContext(request,{'debu':request.POST.get('name')})

    return render_to_response("success.html",context)

def karan(request):
    #just a general test page
    context = RequestContext(request,{"output":json.dumps(request.user)})
    return render_to_response("karan.html",context)

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
def lastuser(request):
    
    list_of_users = args = MyCustomProfile.objects.all().order_by('-id')
    list_of_profile_pics = []
    list_of_kit_ids = []

    
    for user in list_of_users:
        user_fb_profile = FacebookCustomUser.objects.get(pk=user.id)
        facebook = OpenFacebook(user_fb_profile.access_token)
        list_of_profile_pics.append({'userdata':{'first_name':user_fb_profile.first_name,'last_name':user_fb_profile.last_name,'newuid':user.newuid},'image':facebook.my_image_url(size='normal')})

    context = RequestContext(request, {'list_of_profile_pics':list_of_profile_pics})
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
    return StreamingHttpResponse(batcam_iterator())

def batcam_iterator():

    #all_tags = BatCamPictureTag.objects.all()


    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    incoming_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","upload")
    temp_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","temp")
    outgoing_dir_path = os.path.join(BASE_DIR, "static","fbpic","images","output")

    duser = "a"
    i = 0
    

    list_of_filenames = os.listdir(incoming_dir_path) #add if not blank condition here or only file is .gitignore
    
    while list_of_filenames:

        current_filename = list_of_filenames.pop(0)
        current_filename_wihtout_extension = str(current_filename).split(".")[0]
        shutil.move(os.path.join(incoming_dir_path,current_filename), outgoing_dir_path)

        with open("delhi_filenames_current.p","w") as file_handle: #CCCCHANGE
            pickle.dump(list_of_filenames,file_handle)
        
        current_id = current_filename_wihtout_extension

        try:
            current_user = MyCustomProfile.objects.get(newuid__exact=current_id) #CCCCHANGE
        except:
            with open("delhi_skipped.p","a") as out: #CCCCHANGE
                pickle.dump({"filename":current_filename,"user_id":current_id},out)
            i += 1 
            yield str(i) + " Skipped " + str(current_id) + "\n<br />"
            shutil.move(os.path.join(outgoing_dir_path,current_filename), temp_dir_path)
            continue

        duser = current_user.user
        fb = duser.get_offline_graph()

        upload_directory = "static/fbpic/images/output/" #CCCCHANGE

        picture = "http://raiseyourlumia.in/"+ upload_directory + str(current_filename)

        b= dict()
        b['id'] = current_id
        b['name'] = duser.first_name+" "+duser.last_name
        b['picture'] = picture

        try:
            b['response'] = fb.set('me/photos', url=picture, message="Got clicked by the drone. Only need to #RaiseYourLumia")
        except Exception, e:
            b['response'] = str(e)
            b['error']="error generated"
        except:
            b['response'] = "generic error for this person. Please contact Tanuj."
            b['error']="error generated"

        
        
        with open("fb_dump_delhi_log.p","a") as out:
            pickle.dump(b,out)

        i += 1 

        yield str(i) + " " + pickle.dumps(b) + "\r\n<br />"

@csrf_protect
def reRegister(request,batcam_original_id):
    batcam_user = MyCustomProfile.objects.get(batcam_id__exact=batcam_original_id)
    context = RequestContext(request,{"facebook_response":str(batcam_user.id)+" "+str(batcam_user.user.first_name)+" "+str(batcam_user.user.last_name)})
    return render_to_response("uploader.html",context)
