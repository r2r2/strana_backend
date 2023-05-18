import time

from django.core.files.storage import default_storage
from django.db.models import F
from .models import Building, Section, Floor
import zipfile
from mimetypes import guess_type


def calculate_building_min_flat_prices():
    room_params = {
        f"flats_{rooms_count}_min_price": F(f"flats_{rooms_count}_min_price_a")
        for rooms_count in range(5)
    }
    buildings = Building.objects.annotate_min_prices()
    buildings.update(**room_params)


def calculate_building_finish_dates():
    buildings = Building.objects.annotate_finish_dates()
    buildings.update(built_year=F("built_year_a"), ready_quarter=F("ready_quarter_a"))


def calculate_section_min_flat_prices():
    room_params = {
        f"flats_{rooms_count}_min_price": F(f"flats_{rooms_count}_min_price_a")
        for rooms_count in range(5)
    }
    sections = Section.objects.annotate_min_prices()
    sections.update(**room_params)


def calculate_floor_min_flat_prices():
    room_params = {
        f"flats_{rooms_count}_min_price": F(f"flats_{rooms_count}_min_price_a")
        for rooms_count in range(5)
    }
    floors = Floor.objects.annotate_min_prices()
    floors.update(**room_params)


def calculate_current_level():
    buildings = Building.objects.annotate_current_level()
    buildings.update(current_level=F("current_level_a"))


def building_archive_handler(building_id: int):
    """Обработчик загруженных файлов.

    Распаковывает архив и загружает файлы на AWS.
    """
    time.sleep(10)
    instance = Building.objects.get(pk=building_id)
    try:
        compressed = zipfile.ZipFile(instance.panorama_file.file)
    except zipfile.BadZipfile:
        instance.panorama_url = "Файл не является архивом или поврежден"
        instance.save()
        return
    for arch_file in compressed.namelist():
        if arch_file.endswith("/"):
            continue
        storage_file = default_storage.open(f"b/b/p/{arch_file}", "w")
        storage_file.write(compressed.read(arch_file))
        storage_file.close()
        if guess_type(arch_file.split("/")[0])[0] == "text/html" and "/" not in arch_file:
            instance.panorama_url = default_storage.url(storage_file.name)
    if not instance.panorama_url:
        instance.panorama_url = "В архиве не найден корневой HTML файл"
    instance.save()
