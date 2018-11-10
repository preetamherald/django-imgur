from django.contrib import admin
from imgur_testing.models import Person

class PersonAdmin(admin.ModelAdmin):
    list_display = ('image',)
    
    def image(self, obj):
        if obj.photo:
            return '<img src="%s">' % obj.photo.url
        return ''
    image.allow_tags = True

admin.site.register(Person, PersonAdmin)
