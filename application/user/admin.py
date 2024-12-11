from django.contrib import admin
from .models import User

# Register your models here.
admin.site.register(User)

admin.site.site_header = 'BUAACanteen管理员界面'
admin.site.site_title = 'BUAACanteen'






