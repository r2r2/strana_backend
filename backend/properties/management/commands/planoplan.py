from django.core.management import BaseCommand
import xml.etree.ElementTree as ET
from ...models import Property


class Command(BaseCommand):
    def handle(self, *args, **options):
        planoplan = open("12_pretty.xml")
        print(planoplan)
        xml = planoplan.read()
        root = ET.fromstring(xml)
        print(root.attrib)
        property_list = []
        for i in root:
            ids = i.attrib.get("internal-id", None)
            custom_field = i.findall("custom-field")
            for j in custom_field:
                field = j.find("field")
                if field.text == "pbcf_5cb9a523bd89a":
                    url = j.find("value")
                    print(ids, url, url.text)
                    if url.text:
                        property_list.append(Property(id=ids, planoplan=url.text))
        print(Property.objects.bulk_update(property_list, ["planoplan"]))
