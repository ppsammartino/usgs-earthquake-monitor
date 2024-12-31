from datetime import datetime
from math import ceil

from django.core.cache import cache
from django.db import IntegrityError
from django.utils.dateparse import parse_date
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from geopy.distance import geodesic
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.earthquake.models import City, EarthquakeSearchResult
from api.earthquake.serializers import CitySerializer, EarthquakeSearchResultSerializer
from api.earthquake.services import fetch_earthquakes, find_nearest_earthquake


class CityView(APIView):
    """
    Provides endpoints to create and list cities.

    This view allows the user to add new cities (with their coordinates) and
    retrieve all existing cities in the database.
    """

    @swagger_auto_schema(request_body=CitySerializer, responses={201: CitySerializer})
    def post(self, request: Request) -> Response:
        """
        Handles POST requests to create a new city with the given attributes.

        Args:
            request (Request): The request object containing city data.

        Returns:
            Response: A response with the newly created city data if successful,
            or an error message with appropriate HTTP status code if validation fails.
        """
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            try:
                city = serializer.save()
                return Response(CitySerializer(city).data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"error": "City already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: Request) -> Response:
        """
        Handles GET requests to list all available cities.

        Args:
            request (Request): The request object.

        Returns:
            Response: A JSON response with a list of all cities and their details.
        """
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EarthquakeSearchResultPagination(PageNumberPagination):
    """
    Custom pagination for listing all EarthquakeSearchResult records.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request)

        total_pages = ceil(total_count / page_size) if page_size else 1

        return Response(
            {
                "count": total_count,
                "total_pages": total_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


class EarthquakeSearchView(APIView):
    """
    Provides an endpoint for searching earthquakes related to a particular city and date range.

    This view queries the USGS Earthquake API for earthquakes above a specified magnitude (default 5.0)
    occurring between the given start and end dates. It finds the nearest earthquake to the given city,
    caches the result, and returns it in a structured JSON format.

    The cache prevents repeated external API calls for the same query.
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Results limit per page",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "order",
                openapi.IN_QUERY,
                description="Sort order: asc or desc",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: openapi.Response(description="OK")},
    )
    def get(self, request):
        """
        Returns the entire history of EarthquakeSearchResult records, paginated.
        Query params:
          - page (int, optional)
          - page_size (int, optional)
          - order (str, optional) => "asc" or "desc" for sorting by created_at.
        """
        order_param = request.GET.get("order", "desc").lower()  # default is desc
        order_by = "created_at"
        if order_param == "desc":
            order_by = "-created_at"

        queryset = EarthquakeSearchResult.objects.order_by(order_by)

        paginator = EarthquakeSearchResultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = EarthquakeSearchResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["city_id", "start", "end"],
            properties={
                "city_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "start": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                "end": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            },
        )
    )
    def post(self, request):
        """
        Takes parameters {city_id, start, end} in request body.
            1) If EarthquakeSearchResult already exists for those parameters, return it.
            2) Otherwise, do the external search logic:
               - fetch_earthquakes
               - find_nearest_earthquake
               - create EarthquakeSearchResult record
               - return new result
        """
        city_id = request.data.get("city_id")
        start_str = request.data.get("start")
        end_str = request.data.get("end")

        if not (city_id and start_str and end_str):
            return Response(
                {"error": "Must provide city_id, start, and end in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate & fetch city
        try:
            city = City.objects.get(id=city_id)
        except City.DoesNotExist:
            return Response({"error": "City not found"}, status=status.HTTP_404_NOT_FOUND)

        # Parse dates
        start_date = parse_date(start_str)
        end_date = parse_date(end_str)
        if not start_date or not end_date or start_date > end_date:
            return Response({"error": "Invalid start/end date"}, status=status.HTTP_400_BAD_REQUEST)

        # Check cache for quicker response
        cache_key = f"earthquake:{city_id}:{start_str}:{end_str}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Check if there's an existing EarthquakeSearchResult for these params
        existing_result = EarthquakeSearchResult.objects.filter(
            city=city, start_date=start_date, end_date=end_date
        ).first()

        if existing_result:
            # Return existing record
            serializer = EarthquakeSearchResultSerializer(existing_result)
            cache.set(cache_key, serializer.data, 3600)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2) Not found -> proceed with external fetch logic
        try:
            eq_data = fetch_earthquakes(start_date, end_date, min_magnitude=5.0)
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch earthquakes: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        nearest = find_nearest_earthquake(city.latitude, city.longitude, eq_data)

        new_rec = EarthquakeSearchResult(
            city=city,
            start_date=start_date,
            end_date=end_date,
            raw_earthquake_data=nearest or {},
        )

        if nearest:
            props = nearest["properties"]
            new_rec.nearest_earthquake_location = props["place"]
            new_rec.nearest_earthquake_magnitude = props["mag"]
            dt_utc = datetime.utcfromtimestamp(props["time"] / 1000.0)
            new_rec.nearest_earthquake_time = dt_utc
            eq_lat = nearest["geometry"]["coordinates"][1]
            eq_lon = nearest["geometry"]["coordinates"][0]
            new_rec.distance_km = geodesic((city.latitude, city.longitude), (eq_lat, eq_lon)).km

        new_rec.save()
        serializer = EarthquakeSearchResultSerializer(instance=new_rec)

        cache.set(cache_key, serializer.data, timeout=3600)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
