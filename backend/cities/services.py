from django.db.models import F
from django.db.models.functions import Lower
from .models import City


def calculate_city_min_mortgages():
    cities = City.objects.annotate_min_mortgages()
    cities.update(
        min_mortgage_commercial=Lower(F("min_mortgage_commercial_a")),
        min_mortgage_residential=Lower(F("min_mortgage_residential_a")),
        min_mortgage_residential_standard=Lower(F("min_mortgage_residential_standard_a")),
        min_mortgage_residential_support=Lower(F("min_mortgage_residential_support_a")),
        min_mortgage_residential_family=Lower(F("min_mortgage_residential_family_a")),
    )


def calculate_city_min_commercial_price():
    cities = City.objects.annotate_min_commercial_price()
    cities.update(
        min_commercial_price=F("min_commercial_price_a"),
        min_commercial_price_divided=F("min_commercial_price_divided_a")
    )


def calculate_city_commercial_area_ranges():
    cities = City.objects.annotate_commercial_area_ranges()
    cities.update(
        min_commercial_area=F("min_commercial_area_a"),
        max_commercial_area=F("max_commercial_area_a"),
    )


def calculate_city_min_flat_prices():
    room_params = {
        f"flats_{rooms_count}_min_price": F(f"flats_{rooms_count}_min_price_a")
        for rooms_count in range(5)
    }
    cities = City.objects.annotate_min_prices()
    cities.update(**room_params)
