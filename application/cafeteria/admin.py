from django.contrib import admin
from .models import Cafeteria, Dish, Counter


admin.site.register(Dish)
admin.site.register(Counter)
admin.site.register(Cafeteria)

