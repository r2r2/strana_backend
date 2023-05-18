import os
import requests
import traceback
import xml.etree.ElementTree as ET

from tempfile import NamedTemporaryFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile, File
from django.core.files.storage import default_storage
from django.core.management import BaseCommand
from django.db.models import FileField, Q
from django.db.models.fields.files import FieldFile

from buildings.models import Floor, Section
from ...constants import PropertyType, PropertyStatus
from ...models import Property


def parsing_tumen_zvezdniy_mars():
    b4 = "Страна/Тюмень/Звездный/Квартиры/done Марс (готов)"
    buildings = os.listdir(path=b4)
    c = 0
    for b in buildings:
        if b == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{b}/")
        for f in floors:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{b}/{f}")
            for p in plans:
                if p == ".DS_Store":
                    continue
                section_number, floors_number, number = p.split("-")
                number, _ = number.split("_")
                floors = Floor.objects.filter(
                    section__building=26458, number=floors_number, section__number=section_number,
                )
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(section_number, floors_number, number)
                    c += property.count()
                    # for i in property:
                    #     file = FieldFile(i, i.plan, p).name
                    #     with default_storage.open(file, "w") as svg_file:
                    #         svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
                    #     i.plan = file
                    #     i.save()
    print(c)


def parsing_tumen_zvezdniy_merkyri():
    b4 = "Страна/Тюмень/Звездный/Квартиры/done Меркурий (готов)/building_1"
    plans = os.listdir(path=b4)
    # for f in floors:
    #     if f == ".DS_Store":
    #         continue
    #     plans = os.listdir(path=f"{b4}/{f}")
    for p in plans:
        if p == ".DS_Store":
            continue
        building_number, floors_number, number = p.split("-")
        number, _ = number.split("_")
        floors = Floor.objects.filter(section__building=16574, number=floors_number)
        property = Property.objects.filter(
            floor_id__in=floors.values_list("id", flat=True),
            number_on_floor=int(number),
            type=PropertyType.FLAT,
        )
        if property.exists():
            print(building_number, floors_number, number)
            for i in property:
                file = FieldFile(i, i.plan, p).name
                with default_storage.open(file, "w") as svg_file:
                    svg_file.write(open(f"{b4}/{p}").read())
                i.plan = file
                i.save()


def parsing_tumen_zvezdniy_satyrn():
    b4 = "Страна/Тюмень/Звездный/Квартиры/done Сатурн (2 секции из 5)"
    # for b in ["done building_1", "done building_2"]:
    #     if b == ".DS_Store":
    #         continue
    #     floors = os.listdir(path=f"{b4}/{b}/")
    #     for f in floors:
    #         if f == ".DS_Store":
    #             continue
    #         plans = os.listdir(path=f"{b4}/{b}/{f}")
    #         for p in plans:
    #             if p == ".DS_Store" or ".svg" not in p:
    #                 continue
    #             print(p)
    #             number, _ = p.split("_")
    #             section, floor, number = number.split("-")
    #             floors = Floor.objects.filter(
    #                 section__building=30628, number=floor, section__number=section
    #             )
    #             property = Property.objects.filter(
    #                 floor_id__in=floors.values_list("id", flat=True),
    #                 number_on_floor=int(number),
    #                 type=PropertyType.FLAT,
    #             )
    #             if property.exists():
    #                 print(section, number, property)
    #                 for i in property:
    #                     print(p, i.number_on_floor, i.area)
    #                     file = FieldFile(i, i.plan, p).name
    #                     with default_storage.open(file, "w") as svg_file:
    #                         svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
    #                     i.plan = file
    #                     i.save()
    for b in ["done building_3", "done building_4", "done building_5"]:
        if b == ".DS_Store":
            continue
        section = b.split("_")[1]
        floors = os.listdir(path=f"{b4}/{b}/")
        for f in floors:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{b}/{f}")
            floor = f.split("_")[1]
            for p in plans:
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                print(p)
                number, *other = p.split("_")
                number = number[0]
                print(other)
                area = other[0].split("-")[1]
                floors = Floor.objects.filter(
                    section__building=30628, number=floor, section__number=section
                )
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True),
                    number_on_floor=int(number),
                    area=float(area),
                    type=PropertyType.FLAT,
                )
                print(section, floor, area, number, property)
                if property.exists():
                    c = 0
                    for i in property:
                        print(p, i.number_on_floor, i.area)
                        file = FieldFile(i, i.plan, p).name
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_piter_princip():
    b4 = "Страна/Питер/Принцип (не готово)/Квартиры"
    buildings = os.listdir(path=b4)
    c = 0
    for b in buildings:
        if b == ".DS_Store":
            continue
        section = b.split("_")[1]
        floors = os.listdir(path=f"{b4}/{b}")
        for f in floors:
            if f == ".DS_Store":
                continue
            _, floors_number = f.split("_")
            plans = os.listdir(path=f"{b4}/{b}/{f}")
            for p in plans:
                if p == ".DS_Store" or "S.svg" in p:
                    continue
                floor, number, area, *_ = p.split("_")
                floors = Floor.objects.filter(
                    section__building=30705, number=floors_number, section__number=section
                )
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True),
                    number_on_floor=int(number),
                    area=area,
                    type=PropertyType.FLAT,
                )
                if property.exists():
                    for i in property:
                        print(i.number_on_floor, i.area)
                        file = FieldFile(i, i.plan, p).name
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_piter_princip_comm():
    "backend/Страна/Питер/Принцип (не готово)/Коммерция/done building_1"
    b4 = "коммерция/питер_комерц"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{building}")
        for f in floors:
            if f == ".DS_Store":
                continue
            _, floors_number = f.split("_")
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or "S.svg" in p or "pdf" in p:
                    continue
                floor, number, area, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=30705, number=floors_number, section__number=section
                )
                print(p, floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    number_on_floor=int(number),
                    type=PropertyType.COMMERCIAL,
                )
                if property.exists():
                    for i in property:
                        print(i.number_on_floor, i.area)
                        # file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        # with default_storage.open(file, "w") as svg_file:
                        #     svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        # i.plan = file
                        # i.save()


def parsing_tumen_kvartal_moscow():
    b4 = "Страна/Тюмень/Квартал на Московском (не готово)/Квартиры"
    buildings = os.listdir(path=b4)
    b_dict = {"ГП-1": 24453, "ГП-2": 24520}
    for f in buildings:
        if f == ".DS_Store":
            continue
        building, *b_other = f.split("_")
        plans = os.listdir(path=f"{b4}/{f}")
        for p in plans:
            # print(f, p)
            q = Q()
            if p == ".DS_Store" or ".svg" not in p:
                continue
            if building == "ГП-1":
                section = b_other[0].split(" ")[0]
                q &= Q(section__number=section)
                floor = b_other[1].split(" ")[0]
                floor = floor.split("-")
                if len(floor) == 2:
                    floor = [i for i in range(int(floor[0]), int(floor[1]) + 1)]
                    q &= Q(number__in=floor)
                else:
                    q &= Q(number=floor[0])
            elif building == "ГП-2":
                # print(b_other)
                floor = b_other[0].replace("этаж", "").split(" ")[0]
                # print(floor)
                floor = floor.split("-")
                if len(floor) == 2:
                    floor = [i for i in range(int(floor[0]), int(floor[1]) + 1)]
                    q &= Q(number__in=floor)
                else:
                    q &= Q(number=floor[0])
            floors = Floor.objects.filter(section__building=b_dict[building]).filter(q)
            number, area = p.split("_")
            area = area.replace(".svg", "")
            print(q, floors.values_list("id", flat=True), number, area)
            property = Property.objects.filter(
                floor_id__in=floors.values_list("id", flat=True), area=float(area),
            )
            if property.exists():
                print(property)
                for i in property:
                    file = FieldFile(i, i.plan, p).name
                    with default_storage.open(file, "w") as svg_file:
                        svg_file.write(open(f"{b4}/{f}/{p}").read())
                    i.plan = file
                    i.save()


def parsing_tumen_kolumb():
    b4 = "Страна/Тюмень/Колумб/Квартиры/Дом Первый"
    buildings = os.listdir(path=b4)
    for build in buildings:
        if build == ".DS_Store":
            continue
        floors_dir = os.listdir(path=f"{b4}/{build}")
        for f in floors_dir:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{build}/{f}")
            for p in plans:
                # print(p)
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                section, floor, number = p.split("-")
                floors = Floor.objects.filter(
                    section__building=28408, number=floor, section__number=section
                )
                number = number.split("_")[0]
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(property)
                    for i in property:
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{build}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_santa_maria():
    b4 = "Страна/Тюмень/Колумб (не готово)/Квартиры/Санта Мария"
    buildings = os.listdir(path=b4)
    for f in buildings:

        if f == ".DS_Store":
            continue
        section = f.split("_")[-1]
        db = os.listdir(path=f"{b4}/{f}")
        for b in db:
            if b == ".DS_Store":
                continue
            q = Q()
            floor = b.split("_")[1]
            floor = floor.split("-")
            if len(floor) == 2:
                floor = [i for i in range(int(floor[0]), int(floor[1]) + 1)]
                q &= Q(number__in=floor)
            else:
                q &= Q(number=floor[0])
            plans = os.listdir(path=f"{b4}/{f}/{b}")
            for p in plans:
                # print(p)
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                # print(f"{b4}/{f}/{b}/{p}")
                floors = Floor.objects.filter(
                    section__building=79593, section__number=section
                ).filter(q)
                print(q, floors)
                number = p.split("_")[2]
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(property)
                    for i in property:
                        file = FieldFile(i, i.plan, p).name
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{f}/{b}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_sibir_neft():
    b4 = "Страна/Тюмень/Сердце Сибири/Квартиры/Квартал Нефтяников"
    buildings = os.listdir(path=b4)
    for f in buildings:

        if f == ".DS_Store":
            continue
        db = os.listdir(path=f"{b4}/{f}")
        for b in db:
            if b == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{f}/{b}")
            for p in plans:
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                section_number, floors_number, number = p.split("-")
                floors = Floor.objects.filter(
                    section__building=63667, section__number=section_number, number=floors_number
                )
                number = number.split("_")[0]
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(property)
                    for i in property:
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{f}/{b}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_2_zvezdniy_mars():
    b4 = "Страна/Тюмень/Звездный/Квартиры/Марс"
    buildings = os.listdir(path=b4)
    c = 0
    for b in buildings:
        if b == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{b}/")
        for f in floors:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{b}/{f}")
            for p in plans:
                if p == ".DS_Store":
                    continue
                section_number, floors_number, number = p.split("-")
                number, _ = number.split("_")
                floors = Floor.objects.filter(
                    section__building=26458, number=floors_number, section__number=section_number,
                )
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(section_number, floors_number, number)
                    c += property.count()
                    for i in property:
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
                        i.plan = file
                        i.save()
    print(c)


def parsing_tumen_2_zvezdniy_satyrn():
    b4 = "Звездный/Квартиры/Сатурн"
    for b in ["building_1", "building_2", "building_3", "building_4", "building_5"]:
        section = b.split("_")[1]
        if b == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{b}/")
        for f in floors:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{b}/{f}")
            for p in plans:
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                number, _ = p.split("_")
                _, floor, number = number.split("-")
                floors = Floor.objects.filter(
                    section__building=30628, number=floor, section__number=section
                )
                print("floor = ", floors)
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True),
                    number_on_floor=int(number),
                    type=PropertyType.FLAT,
                )
                if property.exists():
                    print(section, number, property)
                    for i in property:
                        print(p, i.number_on_floor, i.area)
                        file = f"30628_{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_evrop_bereg():
    b4 = "Страна/Тюмень/Европейский берег/Лондон"
    for b in ["building_1", "building_2", "building_3"]:
        if b == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{b}/")
        for f in floors:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{b}/{f}")
            for p in plans:
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                print(p)
                number, _ = p.split("_")
                section, floor, number = number.split("-")
                floors = Floor.objects.filter(
                    section__building=31784, number=floor, section__number=section
                )
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True),
                    number_on_floor=int(number),
                    type=PropertyType.FLAT,
                )
                if property.exists():
                    print(section, number, property)
                    for i in property:
                        print(p, i.number_on_floor, i.area)
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{b}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_kolumb_santa_maria():
    b4 = "Страна/Тюмень/Колумб/Квартиры/Санта Мария"
    buildings = os.listdir(path=b4)
    for build in buildings:
        if build == ".DS_Store":
            continue
        floors_dir = os.listdir(path=f"{b4}/{build}")
        for f in floors_dir:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{build}/{f}")
            for p in plans:
                # print(p)
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                section, floor, number = p.split("-")
                floors = Floor.objects.filter(
                    section__building=79593, number=floor, section__number=section
                )
                number = number.split("_")[0]
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(property)
                    for i in property:
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{build}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_moscow_donsckoy_beketow():
    b4 = "Страна/Москва/Донской квартал (готово)/Апарты/дом Бекетов-2 корпус"
    buildings = os.listdir(path=b4)
    for build in buildings:
        if build == ".DS_Store":
            continue
        floors_dir = os.listdir(path=f"{b4}/{build}")
        for f in floors_dir:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{build}/{f}")
            for p in plans:
                # print(p)
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                section, floor, number = p.split("-")
                floors = Floor.objects.filter(
                    section__building=24441, number=floor, section__number="Бекетов"
                )
                number = number.split("_")[0]
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(property)
                    for i in property:
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{build}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_moscow_donsckoy_shyhow():
    b4 = "Страна/Москва/Донской квартал (готово)/Апарты/дом Шухов-1 корпус"
    buildings = os.listdir(path=b4)
    for build in buildings:
        if build == ".DS_Store":
            continue
        floors_dir = os.listdir(path=f"{b4}/{build}")
        for f in floors_dir:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{build}/{f}")
            for p in plans:
                # print(p)
                if p == ".DS_Store" or ".svg" not in p:
                    continue
                section, floor, number = p.split("-")
                floors = Floor.objects.filter(
                    section__building=24441, number=floor, section__number="Шухов"
                )
                number = number.split("_")[0]
                property = Property.objects.filter(
                    floor_id__in=floors.values_list("id", flat=True), number_on_floor=int(number),
                )
                if property.exists():
                    print(property)
                    for i in property:
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{build}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_santa_maria_comm():
    "backend/коммерция/Санта Мария комм"
    b4 = "коммерция/Санта Мария комм"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{building}")
        for f in floors:
            if f == ".DS_Store":
                continue
            _, floors_number = f.split("_")
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or "S.svg" in p or "pdf" in p:
                    continue
                floor, number, area, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=30705, number=floors_number, section__number=section
                )
                print(p, floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    number_on_floor=int(number),
                    type=PropertyType.COMMERCIAL,
                )
                if property.exists():
                    for i in property:
                        print(i.number_on_floor, i.area)
                        # file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        # with default_storage.open(file, "w") as svg_file:
                        #     svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        # i.plan = file
                        # i.save()


def parsing_commercial_properties():
    xml_data = requests.get(
        "https://pb4988.profitbase.ru/export/profitbase_xml/6a362b2c84e5c9eee0df25f65d42d8bc"
    )
    root = ET.fromstring(xml_data.content.decode("utf-8"))
    ns = {
        "feed": "http://webmaster.yandex.ru/schemas/feed/realty/2010-06",
    }
    for property in root.findall("feed:offer", ns):
        try:
            with NamedTemporaryFile() as plan:
                plan_url = (
                    property.find("feed:image[@type='plan']", ns).text
                    if property.find("feed:image[@type='plan']", ns) is not None
                    else None
                )
                if plan_url:
                    plan_res = requests.get(
                        property.find("feed:image[@type='plan']", ns).text, stream=True
                    )
                    for chunk in plan_res:
                        plan.write(chunk)
                        plan.seek(0)

                pk = int(property.get("internal-id"))
                project_id = int(property.find("feed:object", ns).find("feed:id", ns).text)
                building_id = int(property.find("feed:house", ns).find("feed:id", ns).text)
                section_name = property.find("feed:building-section", ns).text
                section, _ = Section.objects.get_or_create(
                    building_id=building_id, number=section_name, defaults={"name": section_name}
                )
                floor, _ = Floor.objects.get_or_create(
                    section=section, number=int(property.find("feed:floor", ns).text),
                )
                data = {
                    "type": PropertyType.COMMERCIAL,
                    "project_id": project_id,
                    "building_id": building_id,
                    "section": section,
                    "floor": floor,
                    "price": int(property.find("feed:price", ns).find("feed:value", ns).text),
                    "area": float(property.find("feed:area", ns).find("feed:value", ns).text),
                    "number_on_floor": (
                        int(property.find("feed:position-on-floor", ns).text)
                        if property.find("feed:position-on-floor", ns).text
                        else None
                    ),
                    "number": property.find("feed:number", ns).text,
                    "plan_code": (
                        property.find("feed:layout-code", ns).text
                        if property.find("feed:layout-code", ns).text
                        else ""
                    ),
                    "price_per_meter": float(
                        property.find("feed:price-meter", ns).find("feed:value", ns).text
                    ),
                    "balconies_count": (
                        int(property.find("feed:balcony-count", ns).text)
                        if property.find("feed:balcony-count", ns).text
                        else None
                    ),
                    "loggias_count": (
                        int(property.find("feed:loggia-count", ns).text)
                        if property.find("feed:loggia-count", ns).text
                        else None
                    ),
                    "separate_wcs_count": (
                        int(property.find("feed:separated-bathroom-unit", ns).text)
                        if property.find("feed:separated-bathroom-unit", ns).text
                        else None
                    ),
                    "combined_wcs_count": (
                        int(property.find("feed:combined-bathroom-unit", ns).text)
                        if property.find("feed:combined-bathroom-unit", ns).text
                        else None
                    ),
                    "plan": (
                        SimpleUploadedFile(plan_url.split("/")[-1], plan.read())
                        if plan_url
                        else None
                    ),
                    "open_plan": bool(property.find("feed:open-plan", ns).text),
                    "rooms": int(property.find("feed:rooms", ns).text),
                    "status": getattr(
                        PropertyStatus, property.find("feed:status", ns).text, PropertyStatus.FREE
                    ),
                    "facing": (
                        {"Да": True, "На выбор": True, "Нет": False}.get(
                            property.find("feed:facing", ns).text, False
                        )
                    ),
                    "description": (
                        property.find("feed:description", ns).text
                        if property.find("feed:description", ns).text is not None
                        else ""
                    ),
                }

                Property.objects.update_or_create(pk=pk, defaults=data)
                print(f"{pk} OK")

        except Exception as ex:
            print(traceback.print_exc())
            print(f"Ошибка при обновлении объекта {property.get('internal-id')}")


def parsing_tumen_zvezdniy_mars_comm():
    "backend/коммерция/тюмень Звездный/mars"
    b4 = "коммерция/тюмень Звездный/mars"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        number_in_floor = os.listdir(path=f"{b4}/{building}")
        for f in number_in_floor:
            if f == ".DS_Store":
                continue
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or f"plan_{int(f)}.svg" not in p:
                    continue
                floor, number, area, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=26458, number=1, section__number=section
                )
                print(p)
                print(floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    number=int(f),
                    type=PropertyType.COMMERCIAL,
                )
                print(property)
                if property.exists():
                    for i in property:
                        print(i.number, i.area)
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_zvezdniy_mercury_comm():
    "backend/коммерция/тюмень Звездный/mercury"
    b4 = "коммерция/тюмень Звездный/mercury"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        number_in_floor = os.listdir(path=f"{b4}/{building}")
        for f in number_in_floor:
            if f == ".DS_Store" or "pdf" in f:
                continue
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or f"plan_{f}.svg" not in p or "pdf" in p:
                    continue
                floor, number, area, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=16574, number=1, section__number=section
                )
                print(p)
                print(floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    number=int(f),
                    type=PropertyType.COMMERCIAL,
                )
                print(property)
                if property.exists():
                    for i in property:
                        print(i.number, i.area)
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_zvezdniy_saturn_comm():
    "backend/коммерция/тюмень Звездный/saturn"
    b4 = "коммерция/тюмень Звездный/saturn"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        number_in_floor = os.listdir(path=f"{b4}/{building}")
        for f in number_in_floor:
            if f == ".DS_Store" or "pdf" in f:
                continue
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or f"plan_{int(f)}.svg" not in p or "pdf" in p:
                    continue
                floor, number, area, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=30628, number=1, section__number=section
                )
                print(p)
                print(floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    number=int(f),
                    type=PropertyType.COMMERCIAL,
                )
                print(property)
                if property.exists():
                    for i in property:
                        print(i.number, i.area)
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_tumen_kolumb_santa_maria_comm():
    "backend/коммерция/Санта Мария комм"
    b4 = "коммерция/Санта Мария комм"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{building}")
        for f in floors:
            if f == ".DS_Store" or "pdf" in f:
                continue
            floor_number = f.split("_")[1]
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or "pdf" in p:
                    continue
                _, _, number, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=79593, number=int(floor_number), section__number=section
                )
                print(p)
                print(floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    number=int(number),
                    type=PropertyType.COMMERCIAL,
                )
                print(property)
                if property.exists():
                    for i in property:
                        print(i.number, i.area)
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        i.plan = file
                        i.save()


def parsing_piter_princip_comm_2():
    "backend/коммерция/питер_комерц"
    b4 = "коммерция/питер_комерц"
    buildings = os.listdir(path=b4)
    for building in buildings:
        section = building.split("_")[1]
        if building == ".DS_Store":
            continue
        floors = os.listdir(path=f"{b4}/{building}")
        for f in floors:
            if f == ".DS_Store" or "pdf" in f:
                continue
            floor_number = f.split("_")[1]
            plans = os.listdir(path=f"{b4}/{building}/{f}")
            for p in plans:
                if p == ".DS_Store" or "pdf" in p or "S.svg" in p:
                    continue
                _, _, area, *_ = p.split("_")
                floors_query = Floor.objects.filter(
                    section__building=30705, number=int(floor_number), section__number=section
                )
                print(p)
                print(floors_query)
                property = Property.objects.filter(
                    floor_id__in=floors_query.values_list("id", flat=True),
                    area=float(area),
                    type=PropertyType.COMMERCIAL,
                )
                print(property)
                if property.exists():
                    for i in property:
                        print(i.number, i.area)
                        file = f"{i.id}_{FieldFile(i, i.plan, p).name}"
                        with default_storage.open(file, "w") as svg_file:
                            svg_file.write(open(f"{b4}/{building}/{f}/{p}").read())
                        i.plan = file
                        i.save()


class Command(BaseCommand):
    def handle(self, *args, **options):

        # parsing_piter_princip()
        # parsing_piter_princip_comm()

        # parsing_tumen_kvartal_moscow()
        # parsing_tumen_kolumb()
        # parsing_tumen_kolumb_santa_maria()
        # parsing_tumen_sibir_neft()
        # parsing_tumen_evrop_bereg() # Done

        # parsing_tumen_2_zvezdniy_mars()
        # parsing_tumen_2_zvezdniy_merkyri()
        # parsing_tumen_2_zvezdniy_satyrn()
        # parsing_moscow_donsckoy_beketow()
        # parsing_moscow_donsckoy_shyhow()

        # parsing_commercial_properties()
        # parsing_tumen_zvezdniy_mars_comm()
        # parsing_tumen_zvezdniy_mercury_comm()
        # parsing_tumen_zvezdniy_saturn_comm()
        # parsing_tumen_kolumb_santa_maria_comm()

        parsing_piter_princip_comm_2()

        pass
