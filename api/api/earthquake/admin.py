from django.contrib import admin

from .models import City, EarthquakeSearchResult

# Registering models in admin
admin.site.register(City)
admin.site.register(EarthquakeSearchResult)
