from decimal import Decimal
from typing import Optional

from dadata import Dadata
from django.conf import settings
from haversine import haversine

from cities.models import City
from location.models import IPLocation


def get_location(ip_address: str) -> Optional[City]:
    """Определение города по IP адресу.

    Для получения координат по IP адресу используется сервис Dadata, данные кэшируются в модели IPLocation,
        далее производится поиск ближайшего города по координатам с использованием библиотеки SciPy.
    """

    if location := IPLocation.objects.filter(ip_address=ip_address).last():
        return location.city
    dadata = Dadata(settings.DADATA['TOKEN'], settings.DADATA['SECRET'])
    result = dadata.iplocate(ip_address)
    if not result or 'data' not in result.keys():
        return None
    current_geo = (Decimal(result['data']['geo_lat']), Decimal(result['data']['geo_lon']))
    qs = City.objects.filter(active=True, latitude__isnull=False, longitude__isnull=False).values('latitude', 'longitude')
    citi_coordinates = [((item['latitude']), (item['longitude'])) for item in list(qs)]
    distances = []
    for coord in citi_coordinates:
        distances.append(haversine(coord, current_geo))
    item_idx = distances.index(min(distances))
    city = City.objects.filter(latitude=citi_coordinates[item_idx][0], longitude=citi_coordinates[item_idx][1]).last()
    IPLocation.objects.create(ip_address=ip_address, city=city)
    return city
