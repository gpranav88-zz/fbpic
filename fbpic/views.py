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
from random import randint
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
    list_of_ids = [4299,4300,4301,4302,4303,4304,4305,2469,2470,2471,2472,2473,2474,2475,2476,2477,2478,2479,2480,2481,2482,2105,2106,2107,2108,2109,4254,2154,2647,2648,2649,2650,2104,2103,2102,2101,2155,2157,2156,2158,2159,2160,2161,2162,2163,2164,2165,2166,2167,2168,2601,2602,2603,2604,2605,2606,2607,2608,2609,2610,2611,2612,2613,2614,2615,2616,2617,2618,2619,2620,2621,2622,2623,2624,2625,2626,2627,2628,2629,2630,2631,2632,2633,2634,2635,2636,2637,2638,2639,2640,2641,2642,2643,2644,2645,2646,2181,2180,2179,2178,4834,4833,4832,4881,4880,4879,4878,4877,4876,4875,4874,4873,4872,4871,4870,4869,4868,4867,4866,4865,4864,4863,4862,4861,4860,4859,4858,4857,4856,4855,4854,4853,4852,4851,4850,4849,4848,4847,4846,4845,4844,4843,4842,4841,4840,4839,4838,4837,4836,4679,4516,4517,4518,4519,4520,4521,4522,4523,4524,4525,4526,4527,4528,4529,4530,4531,4532,4533,4534,4535,4536,4537,4538,4539,4540,4541,4542,4543,4544,4545,4546,4547,4548,4549,4550,4551,4552,4553,4554,4555,4556,4557,4558,4559,4560,4561,4562,4563,4564,4565,3951,3952,3953,3954,3955,3956,3957,3958,3959,3960,3961,3962,3963,3964,3965,3966,3967,3968,3969,3970,3971,3972,3973,2493,2494,2495,2496,2497,2498,2499,2500,2501,2502,2503,2504,2505,2506,2507,2508,2509,2510,2511,2512,2513,2514,2515,2516,2517,2518,2519,2520,4678,4677,4676,2851,4291,4460,4459,4458,4457,4456,4455,4454,4453,4452,4451,4450,4449,4448,4447,4446,4445,4444,4443,2417,2416,3834,3835,3836,3837,3838,3839,3840,3841,3842,3843,3844,3845,3846,3847,3848,3849,3850,3851,3852,3853,3854,2902,2903,2904,2905,2906,2907,2908,2909,2910,2911,2912,2913,2914,2915,2916,2917,2918,2919,2920,2921,2922,2923,2924,2925,2926,2927,2928,3974,3975,3976,3977,3978,3979,3980,3981,3982,3983,3984,3985,3986,3987,3988,3989,3990,2492,2491,2490,2489,2488,2487,2486,2485,2484,2483,2364,2250,2249,2248,2247,2246,2245,2244,2243,2242,2241,4674,4675,2240,2239,2238,2237,2236,2235,2234,2233,2232,2231,2230,2229,2228,2227,2226,2225,2224,2223,2222,2221,2220,2219,2218,2217,2216,2215,2214,2213,2212,2211,2210,2209,2208,2207,2206,4935,4934,2379,2378,2377,2376,2375,2374,2373,2372,2371,2370,2369,2368,2367,2366,2365,3466,3467,3468,3469,3470,3471,3472,3473,3474,3475,3476,3477,3478,3479,3480,3481,3482,3483,3484,3485,3486,3487,3488,3489,3490,3491,3492,3493,3494,3495,3496,3497,3498,3499,3500,1957,1958,1959,1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987]
    
    
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
        
        list_of_ids = str(current_filename_wihtout_extension).split("-")


        for current_id in list_of_ids:
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

            messages = ["The drone just caught me. Here is my picture. #RaiseYourLumia",
"Here I am getting snapped by drone. #RaiseYourLumia",
"This is crazy me, caught by the drone at #MicrosoftVfest  #RaiseYourLumia",
"The eye in the sky just caught me. #RaiseYourLumia",
"Me and my world around, just snapped by drone. #RaiseYourLumia"]

            try:
                b['response'] = fb.set('me/photos', url=picture, message=messages[randint(0,4)])
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
