# django-imgur
> for python 3.x modified by /preetamherald

# use

with this, you'll be able to save user uploded images to imgur and save its link in your database.

# What

django-imgur is a Django App that contains a Django Storage which uses Imgur.
Inspired, based, and forked from [django-dropbox](https://github.com/andres-torres-marroquin/django-dropbox)

# Installing

## First of all

    pip install -e git+http://github.com/preetamherald/django-imgur#egg=django-imgur

## Add it to your Django Project

INSTALLED_APPS on settings.py
s
    INSTALLED_APPS = (
        ...
        'django_imgur',
        ...
    )

additionally you must need to set the next settings:

    IMGUR_CONSUMER_ID = "xxx"
    IMGUR_CONSUMER_SECRET = "xxx"
    IMGUR_USERNAME = "xxx"
    IMGUR_ACCESS_TOKEN = "xxx"
    IMGUR_ACCESS_TOKEN_REFRESH = "xxx"

if you don't have `IMGUR_CONSUMER_ID` or `IMGUR_CONSUMER_SECRET` 
you will need to create an Imgur app 
then set `IMGUR_CONSUMER_ID` and `IMGUR_CONSUMER_SECRET` settings in `settings.py`,
after that run:

    $ python manage.py get_imgur_token

And follow up on screen instructions, finally set the `IMGUR_ACCESS_TOKEN` and `IMGUR_USERNAME` in `settings.py`

add to your models

    from django.db import models
    from django_imgur.storage import ImgurStorage
    
    #...

    STORAGE = ImgurStorage()
    
    #...

    class MyModel(models.Model):
        # ...
        photo = models.ImageField(upload_to='photos', storage=STORAGE, null=True, blank=True)

Make migrations and migrate

    $ python manage.py makemigrations
    $ python manage.py migrate
    
Now add to templates

    <img src="{{ mymodel.photo.url }}">

# made with ♥️ by Preetam Yadav
