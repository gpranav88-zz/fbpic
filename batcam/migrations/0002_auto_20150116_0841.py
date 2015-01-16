# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('batcam', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BatCamPictureTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('complete_path', models.CharField(max_length=200)),
                ('filename', models.CharField(max_length=30)),
                ('batcam_id', models.CharField(max_length=10, null=True, blank=True)),
                ('zone', models.CharField(max_length=1, choices=[(b'B', b'Batcam'), (b'U', b'Untameable'), (b'T', b'Trampoline')])),
                ('timestamp_tag', models.DateTimeField(auto_now_add=True)),
                ('all_user_ids', models.CharField(max_length=70)),
                ('keeper', models.CharField(default=b'U', max_length=1)),
                ('hero', models.CharField(default=b'U', max_length=1)),
                ('posted_to_facebook', models.BooleanField(default=False)),
                ('timestamp_facebook_post', models.DateTimeField(auto_now=True, null=True)),
                ('facebook_post_id', models.CharField(max_length=128, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='BatCamPicture',
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='batcam_day2_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='batcam_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='discard_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='hero_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='keep_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='posted_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='tagged_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='trampoline_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mycustomprofile',
            name='untameable_id',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
