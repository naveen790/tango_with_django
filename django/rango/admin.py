from django.contrib import admin
from rango.models import *

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
    
admin.site.register(Category)
admin.site.register(Page,PageAdmin)
admin.site.register(UserProfile)
