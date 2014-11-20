from django.db import models

# Create your models here.
from django.dispatch.dispatcher import receiver
from django_facebook.models import FacebookModel
from django.db.models.signals import post_save
from django_facebook.utils import get_user_model, get_profile_model
from fbpic import settings

class MyCustomProfile(FacebookModel):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	batcam_id = models.CharField(max_length=10, null = True, blank = True)
	untameable_id = models.CharField(max_length=10, null = True, blank = True)
	trampoline_id = models.CharField(max_length=10, null = True, blank = True)

	@receiver(post_save)

	def create_profile(sender, instance, created, **kwargs):

		"""
		Create a matching profile whenever a user object is created.
		"""
		
		if sender == get_user_model():
			user = instance
			profile_model = get_profile_model()

			if profile_model == MyCustomProfile and created:
				profile, new = MyCustomProfile.objects.get_or_create(user=instance)

class BatCamPicture(models.Model):
	
	PICTURE_TAKEN_AT = (
		('B', 'Batcam'),
		('U', 'Untameable'),
		('T', 'Trampoline'),
	)
	CAMERA_ID = (
		
		('B1', 'Batcam'),
		('U1', 'Untameable 1'),
		('U2', 'Untameable 2'),
		('U3', 'Untameable 3'),
		('U4', 'Untameable 4'),
		('UD', 'Untameable Drone'),
		('T1', 'Trampoline 1'),
		('TD', 'Trampoline Drone'),
		
		)

	complete_path = models.CharField(max_length=70)
	filename = models.CharField(max_length=30)
	user_id = models.CharField(max_length=10, null= True, blank = True )
	zone = models.CharField(max_length=1, choices=PICTURE_TAKEN_AT)
	all_user_ids = models.CharField(max_length=70)

	"""
	cam_id = models.CharField(max_length=2, choices=CAMERA_ID)
	"""
