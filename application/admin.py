from django.contrib import admin
from application.models import *
# Register your models here.
class tableAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'photo_original','photo_original_fichie', 'photo_modifier')
admin.site.register(table, tableAdmin)
