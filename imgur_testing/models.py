from django.db import models
from django_imgur.storage import ImgurStorage

STORAGE = ImgurStorage()

class Person(models.Model):
     photo = models.ImageField(upload_to='photos', storage=STORAGE, null=True, blank=True)
