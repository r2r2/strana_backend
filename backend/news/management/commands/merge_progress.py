from django.core.management import BaseCommand
from ...models import News, NewsType


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = News.objects.filter(type=NewsType.PROGRESS)
        projects = list(set(qs.values_list("projects", flat=True).distinct()))
        for project in projects:
            dates = list(
                qs.filter(projects__in=[project]).values_list("date", flat=True).distinct()
            )
            print(project, " *" * 10)
            for d in dates:
                prog = qs.filter(projects__in=[project], date=d)
                if prog.count() >= 2:
                    prog_original = prog.first()
                    prog_delete = prog.exclude(id=prog_original.id)
                    for p_d in prog_delete:
                        for i in p_d.newsslide_set.all():
                            i.news = prog_original
                            i.save()
                        print(p_d)
                        p_d.published = False
                        p_d.save()
