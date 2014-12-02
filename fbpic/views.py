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
    return StreamingHttpResponse(batcam_iterator())

def batcam_iterator():
    batcam_copies = [ "Just got caught by the eye in the sky! Here's a glimpse from the drone #BatCam",
    "This is awesome! At #BacardiNH7Weekender, Delhi got snapped by the drone #BatCam. ",
    "The drone caught me! Here's my picture by the #BatCam",
    "The Drone just snapped me at #BacardiNH7Weekender, Delhi. #BatCam Check it out!",
    "Here's me getting snapped by the drone at #BacardiNH7Weekender, Delhi. Thank you #BatCam!"]
    #all_tags = BatCamPictureTag.objects.all()
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    #incoming_dir_path = os.path.join(BASE_DIR, "static","fbpic","images",zone,"incoming")
    list_of_filenames = ["1000-4312","1000-4322-4312-3157","1298_2","1298","1318-1329","1323","1324-1334_2","1324-1334","1329","1334-1324","1342_2","1342_3","1342_4","1342","1343","2054","2074","2079","2081","2091-2092","2092-2091","2093-2094","2093","2098-2169-2097-2170","2098-2169-2097","2098","2100","2116","2119-2120","2119","2121","2122-2570-2571_1","2122-2570-2571_200","2122-2570-2571_2","2122-2570-2571","2122-2570","2122","2125","2129","2138-2163-2162","2165_1","2165_200","2165_2","2165-3024_200","2165-3024","2165-4170","2165_5","2165","2166-2168","2167","2168-2166","2169","2180","2181_2","2181","2184","2468_2","2468","2497-2565","2497","2500","2503-2502","2503-2504","2505","2511_200","2511_3","2511_4","2511","2521-252200","2521-2522","2521","2522_2521","2523","2525-2167_1","2525-2167-4222","2525-2167","2525-4222","2527-2139","2532","2534_2","2534","2540_1","2540","2544_2","2544","2553","2558-2561","2559-2560","2561","2562-2117","2564","2567-2497-2566","2567-2497","2568","2569-2568","2570-2571-2522","2570","2571-2570-2122","2581-2186","2593","2594","2595","2596","2600","3012_2","3012","3021-3026-3038","3021_4","3021_5","3021","3024_200","3024-2165","3024_2","3024_5","3024","3025","3026-3027-3028_2","3026-3027-3028_5","3026-3027-3028_6","3026-3027-3028","3026","3027-3026-3028","3027-3028_200","3027-3028","3028-3026","3028","3029-3032_17","3029-3032_5","3029-3032_8","3029-3032","3030-4015","3030","3031-3033_200","3031-3033","3032-3029","3032-3039_2","3033-3031","3033","3034_3","3034-4249","3034-4259-4249_2","3034","3037","3038_2","3038","3039-3036_200","3039-3036_2","3039-3036","3040_200","3040","3083-3084_2","3085_3086","3087-3088","3087","3090-3091","3092","3093","3094","3095-3096","3097","3098","3107-3108","3112_3113_2","3112","3113_2","3113_4","3113","3114_2","3114","3117","3118","3159","3160-3159","3229","3233-3234-3235","4002-4372","4002","4004","4005_2","4005","4007-4052-4278","4007-4052","4007-4278-4052","4007","4009_5","4009","4012-4022","4015_200","4015_5","4015","4018 4432","4018-4432","4018","4019_2","4019","4022-4012","4025-4377-4367-4387","4025","4028-4038","4029-1343","4029_200","4029_2","4029","4032_2","4032","4034","4035-4046","4039-4130_200","4039-4130","4039","4041-4081_2","4041-4081","4041-4309-4081","4042_2","4042","4046-4035","4047-4061-4077","4049-4059","4052-4007-4278","4054_2","4054","4057-4261-4277","4057-4267","4057-4277_2","4057-4277","4057","4058_1341_4338_3038","4058_1341_4338","4058-1341-4338","4058-1342-4338","4058-4338","4059","4061-4071","4064-4091","4067-4047-4077","4069_200","4069","4071-4061-4319","4071-4061","4077-4067-4047","4078-4261_200","4078-4261-4419","4078-4261","4078","4079_200","4079_2","4079","4081-4041","4081-4309-4041","4083","4084-4094","4088","4089","4091-4064","4092","4094_2","4094","4099","4102","4103_1","4103_2","4103-4433","4103","4108_2","4108","4111-4101_2","4111-4101","4111-4427-4437","4112","4113_2","4113","4117","4122","4125-4235_200","4125-4235","4125-4325_2","4126","4130-4039","4130","4135-4155-4210-4190","4135-4155","4135-4210_2","4135-4210","4135","4136","4137","4138_2","4138-4148-4419","4138-4148","4138-4249-3034","4138","4140_200","4140_2","4140","4142","4143-4153","4143","4145-4165","4145","4146","4148-4138_2","4148-4138","4148-4419-4138","4148-4419","4148","4150-4130_2","4150-4130","4150","4151_200","4151","4152-4122_2","4152-4122","4152-4190-4210","4152","4153-4143_2","4153-4143","4153-4210-4190_2","4155_2","4155-4135","4155-4210-4190","4155","4156_5","4156","4157_200","4157","4158","4160-4170_15","4161","4163-4173","4163","4165-4145_200","4165-4145","4167","4168_2","4168","4170_2","4170_3","4170-4160","4170_5","4170_6","4170_7","4170_8","4170","4175-4068","4175","4176","4177-4207_200","4177-4207","4178-4198","4181","4183-4213_2","4183-4213","4185_2","4185","4186-4166","4186","4187","4190-4210_2","4190-4210","4192","4193_2","4193-4233-4213-4203","4193","4195_2","4197","4200_200","4200_2","4200","4202","4203-4193","4203","4207-4177","4210-4135","4210-4136","4210-4155-4190-4135_200","4210-4155-4190-4135_2","4210-4155-4190-4135_3","4210-4155-4190-4135","4210-4190_2","4210-4190_3","4211_1","4211","4212","4215_3","4215-4235","4215","4220_200","4220_2","4220-4165-4230-4145-4200","4220","4221","4222_5","4222","4225_3","4225-4329","4225","4227-4197","4228-4238","4230_200","4230_2","4230_3","4230","4235-4125_2","4235-4125","4237","4243-4253_2","4243-4253","4243","4247","4248_2","4248","4249-3034_3","4249-3034","4249-4259_2","4249-4259","4253-4243","4253-4283","4254-2140","4259-303404249","4259","4261_1","4261_200","4261-4277-4057","4261","4262-2183-4342","4262-2183","4262","4267_2","4267-4277","4267","4269-4279","4273-4343-4253","4277_2","4277-4267","4277","4278","4279-4269","4282","4285-4085","4286","4287_1","4287_2","4287","4288_2","4288_3","4288","4289_25","4289_2","4289_4","4289_5","4289_6","4289_7","4289","4291","4292","4293-4021-4011","4293","4295-4268","4297_2","4297","4300_2","4300","4302_2","4302_3","4302_5","4302","4307-4337","4308","4312-2511-4322","4312-4322-2511_20","4312-4322-2511_30","4312-4322","4315","4317-4394","4317","4319-4061-4071","4320-4299","4321_2","4321_3","4321_4","4321","4322_2","4322-4312-1000","4322-4312-2511","4322","4325-4308","4327","4329","4331-4321-4311","4338-4058_200","4338-4058-4268","4338-4058","4338-4268-4058","4338","4340","4342-2183-4262","4343-4273-4253","4347-4357","4352-4362","4357-4347","4357","4359","4360-4019_2","4360-4019","4372-4002_2","4372-4002","4378-4349","4385","4387-4367-4025-4377","4388","4392-4382","4394_2","4394","4395-4257-4031-4385-4411","4395-4257-4037-4385-4411","4397-4404","4398_200","4398_2","4398_3","4398_4","4398","4399-4009","4404-4397","4407_2","4407","4417-4427-4437","4418-4438","4418","4419-4429","4423","4427-4111-4437","4427","4429-4148-4138-4249-3034-4249-4259","4432-4018","4432","4433_2","4433-4103","4433","4436-4244","4438-4418","4456"]
    duser = "a"
    i = 0
    yield "hi!"

    with open("fb_dump_delhi_log.p","a") as out:
        for current_filename in list_of_filenames:
            list_of_ids = str(current_filename).split("-")
            for current_ids in list_of_ids:
                current_id = int(str(current_ids).split("_")[0])
                try:
                    current_user = MyCustomProfile.objects.get(batcam_id__exact=current_id)
                except:
                    current_user = MyCustomProfile.objects.get(batcam_day2_id__exact=current_id)

                duser = current_user.user
                fb = duser.get_offline_graph()

                upload_directory = "static/fbpic/images/delhi/batcam/"
                zone = "B" ##can be B, U or T

                picture="http://batcam.bacardiindia.in/"+ upload_directory +str(current_filename)+".jpg"

                b= dict()
                b['batcam_id'] = current_id
                b['name'] = duser.first_name+" "+duser.last_name
                b['picture'] = picture

                try:
                    dummy="dumb"
                    b['response'] = fb.set('me/photos', url=picture, message=batcam_copies[random.randint(0, 4)],place="374502716046163")
                except Exception, e:
                    b['response'] = str(e)
                    b['error']="error generated"
                except:
                    b['error']="error generated"

                picture_tag = BatCamPictureTag.objects.create(
                    complete_path = os.path.join(BASE_DIR, upload_directory,str(current_filename)+".jpg"),
                    filename = str(current_filename)+".jpg",
                    batcam_id = current_id,
                    zone = zone,
                    all_user_ids = list_of_ids,
                    posted_to_facebook =True,
                    facebook_post_id = b['response']
                    )
                picture_tag.save()

                pickle.dump(b,out)
                i += 1 
                yield str(i) + " " + pickle.dumps(b) + "\r\n<br />"

@csrf_protect
def reRegister(request,batcam_original_id):
    batcam_user = MyCustomProfile.objects.get(batcam_id__exact=batcam_original_id)
    context = RequestContext(request,{"facebook_response":str(batcam_user.id)+" "+str(batcam_user.user.first_name)+" "+str(batcam_user.user.last_name)})
    return render_to_response("uploader.html",context)
