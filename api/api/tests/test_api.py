from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.earthquake.models import City, EarthquakeSearchResult

dummy_cache_settings = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


class CityViewTestCase(TestCase):
    """
    A test suite covering City endpoints and edge cases
    """

    def setUp(self) -> None:
        """
        Sets up initial test data and a test client.
        """
        self.client = APIClient()
        self.city_endpoint = reverse("cities")
        self.earthquake_endpoint = reverse("earthquakes")

        # Create a sample city to test with
        self.city = City.objects.create(
            name="Los Angeles",
            latitude=Decimal("34.052235"),
            longitude=Decimal("-118.243683"),
        )

    def test_create_city(self) -> None:
        """
        Test creating a new city with valid data.
        """
        payload = {"name": "Tokyo", "latitude": "35.689487", "longitude": "139.691711"}
        response = self.client.post(self.city_endpoint, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["name"], "Tokyo")

    def test_create_city_duplicate(self) -> None:
        """
        Test creating a city that already exists returns a 400 error.
        """
        payload = {
            "name": "Los Angeles",
            "latitude": "34.052235",
            "longitude": "-118.243683",
        }
        response = self.client.post(self.city_endpoint, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_cities(self) -> None:
        """
        Test listing cities returns all created cities.
        """
        response = self.client.get(self.city_endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(any(city["name"] == "Los Angeles" for city in response.data))

    def test_city_serializer_validation(self) -> None:
        """
        Test City creation with invalid data returns 400.
        """
        payload = {"name": "", "latitude": "9999", "longitude": "abc"}
        response = self.client.post(self.city_endpoint, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("latitude", response.data)
        self.assertIn("longitude", response.data)


class EarthquakeSearchViewTestCase(TestCase):
    """
    Test suite for EarthquakeSearchView, covering:
      - GET: List (paginated) of EarthquakeSearchResult
      - POST: Return existing or create new
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("earthquakes")  # e.g. /api/earthquakes/
        self.city = City.objects.create(name="Los Angeles", latitude=Decimal("34.05"), longitude=Decimal("-118.24"))

    def test_no_results_found(self):
        """
        If no EarthquakeSearchResult exist, GET should return an empty paginated list.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # If DRF pagination is used, 'results' key should exist
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)
        # Optionally check 'count', 'next', 'previous'
        self.assertIn("count", data)
        self.assertEqual(data["count"], 0)

    def test_get_non_empty_list(self):
        """
        If EarthquakeSearchResult records exist, GET should return them in a paginated list.
        """
        # Create a sample record
        EarthquakeSearchResult.objects.create(
            city=self.city,
            start_date=date(2021, 6, 1),
            end_date=date(2021, 7, 5),
            nearest_earthquake_location="Near Ojai, CA",
            nearest_earthquake_magnitude=5.1,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        # Check that the item is in the results
        item = data["results"][0]
        self.assertEqual(item["nearest_earthquake_location"], "Near Ojai, CA")
        self.assertEqual(item["nearest_earthquake_magnitude"], 5.1)

    def test_post_missing_fields(self):
        """
        POST without city_id, start, or end should return 400.
        """
        payload = {"start": "2021-06-01"}  # missing end, city_id
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_post_invalid_city(self):
        """
        POST with an invalid city_id should return 404.
        """
        payload = {
            "city_id": 9999,  # city not found
            "start": "2021-06-01",
            "end": "2021-07-05",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    @override_settings(CACHES=dummy_cache_settings)
    def test_post_existing_search(self):
        """
        If EarthquakeSearchResult already exists for (city, start_date, end_date),
        POST should return the existing record with 200, no external fetch.
        """
        existing = EarthquakeSearchResult.objects.create(
            city=self.city,
            start_date=date(2021, 6, 1),
            end_date=date(2021, 7, 5),
            nearest_earthquake_location="Foo",
            nearest_earthquake_magnitude=5.0,
        )
        payload = {"city_id": self.city.id, "start": "2021-06-01", "end": "2021-07-05"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The returned data should match existing
        self.assertEqual(response.data["nearest_earthquake_location"], "Foo")
        self.assertEqual(response.data["nearest_earthquake_magnitude"], 5.0)
        self.assertEqual(response.data["id"], existing.id)

    @patch("api.earthquake.views.find_nearest_earthquake")
    @patch("api.earthquake.views.fetch_earthquakes")
    @override_settings(CACHES=dummy_cache_settings)
    def test_post_new_search(self, mock_fetch, mock_find_nearest):
        """
        If no existing record is found, POST should call external fetch,
        create a new EarthquakeSearchResult, and return 201.
        """
        # Mock fetch_earthquakes to avoid real external calls
        mock_fetch.return_value = {
            "features": [
                {
                    "geometry": {"coordinates": [-118.5, 34.2, 10.0]},
                    "properties": {
                        "time": 1625053800000,  # 2021-06-30T10:30:00Z
                        "place": "Mock Quake",
                        "mag": 5.7,
                    },
                }
            ]
        }
        # Mock find_nearest_earthquake to pick the single feature
        mock_find_nearest.return_value = mock_fetch.return_value["features"][0]

        payload = {"city_id": self.city.id, "start": "2021-06-01", "end": "2021-07-05"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertIn("nearest_earthquake_location", data)
        self.assertEqual(data["nearest_earthquake_location"], "Mock Quake")
        self.assertEqual(data["nearest_earthquake_magnitude"], 5.7)

        # Check that a new record is indeed created in DB
        qs = EarthquakeSearchResult.objects.filter(
            city=self.city, start_date=date(2021, 6, 1), end_date=date(2021, 7, 5)
        )
        self.assertEqual(qs.count(), 1)
        new_rec = qs.first()
        self.assertEqual(new_rec.nearest_earthquake_location, "Mock Quake")
        self.assertEqual(new_rec.nearest_earthquake_magnitude, 5.7)
