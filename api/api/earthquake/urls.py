from django.urls import path

from .views import CityView, EarthquakeSearchView

urlpatterns = [
    path("cities/", CityView.as_view(), name="cities"),
    path("earthquakes/", EarthquakeSearchView.as_view(), name="earthquakes"),
]
