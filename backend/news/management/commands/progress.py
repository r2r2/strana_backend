import requests
from datetime import datetime
from django.core.management import BaseCommand
import xml.etree.ElementTree as ET
from buildings.models import Building
from common.tasks import save_remote_image
from common.utils import transliterate
from projects.models import Project
from ...models import News, NewsSlide
from ...constants import NewsType


class Command(BaseCommand):
    def handle(self, *args, **options):
        response = requests.get("https://strana.com/export/construction.php")
        xml = response.content.decode("utf-8")
        root = ET.fromstring(xml)
        all_progress = root.findall(".//item")
        for indx, i in enumerate(all_progress):
            project = i.find("project-name").text.strip().replace("ё", "е")
            if project == "Донской квартал":
                project = "Донской Квартал"
            project = Project.objects.get(name=project)
            house_name = i.find("house-name").text.strip().replace("(", "").replace(")", "")
            building = Building.objects.filter(name=house_name, project=project).first()
            date_int = int(i.find("date").text)
            date = datetime.fromtimestamp(date_int)
            header = i.find("header").text
            description = i.find("description").text
            if description:
                description = description.replace("<![CDATA[", "").replace("]]>", "")
            else:
                description = ""
            obj, _ = News.objects.get_or_create(
                title=header,
                slug=transliterate(f"{header}-{house_name}-{date_int}"[:49]).replace(" ", "-"),
                type=NewsType.PROGRESS,
                text=description,
                date=date,
                published=True,
            )
            obj.projects.set([project.id])
            obj = News.objects.filter(
                title=header, type=NewsType.PROGRESS, text=description, date=date
            ).first()
            images = i.find("images")
            if images and obj:
                images = images.findall("image")
                if images:
                    if not obj.image:
                        save_remote_image.delay(
                            "news", "News", obj.id, "image", images[0].text,
                        )
                    for j in range(len(images)):
                        ns, _ = NewsSlide.objects.get_or_create(
                            news=obj, building=building, order=j
                        )
                        if not ns.image:
                            save_remote_image.delay(
                                "news", "NewsSlide", ns.id, "image", images[j].text,
                            )
