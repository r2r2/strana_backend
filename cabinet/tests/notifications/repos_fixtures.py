from importlib import import_module

from pytest import fixture

from src.main_page.repos import MainPageTextRepo
from src.notifications.repos import AssignClientTemplateRepo, SmsTemplateRepo


@fixture(scope="function")
def assign_client_template_repo() -> AssignClientTemplateRepo:
    assign_client_template_repo: AssignClientTemplateRepo = getattr(
        import_module("src.notifications.repos"), "AssignClientTemplateRepo"
    )()
    return assign_client_template_repo


@fixture(scope="function")
def main_page_repo() -> MainPageTextRepo:
    main_page_repo: MainPageTextRepo = getattr(
        import_module("src.main_page.repos"), "MainPageTextRepo"
    )()
    return main_page_repo


@fixture(scope="function")
def sms_template_repo() -> SmsTemplateRepo:
    sms_template_repo: SmsTemplateRepo = getattr(
        import_module("src.notifications.repos"), "SmsTemplateRepo"
    )()
    return sms_template_repo


@fixture(scope="function")
def sms_template_factory(sms_template_repo, faker):
    async def sms_template(i=0, is_active=True):
        data = {
            "template_text": faker.text(),
            "sms_event": f"test_event_{i}",
            "sms_event_slug": f"test_event_slug_{i}",
            "is_active": is_active,
        }
        return await sms_template_repo.create(data)

    return sms_template


@fixture(scope="function")
async def sms_template(sms_template_repo, faker, is_active=True):
    data = {
        "template_text": faker.text(),
        "sms_event": f"test_event_{faker.random_int(min=0, max=15)}",
        "sms_event_slug": f"test_event_slug_{faker.bothify(letters='ABCDE')}",
        "is_active": is_active,
    }
    template = await sms_template_repo.create(data)
    return template


@fixture(scope="function")
def assign_client_template_factory(
        assign_client_template_repo,
        faker,
        city,
        sms_template,
):
    async def assign_client_template(i=0, default=False):
        data = {
            "title": f"test_{i}",
            "name": faker.name(),
            "text": faker.text(),
            "success_assign_text": faker.text(),
            "success_unassign_text": faker.text(),
            "default": default,
            "city": city,
            "sms": sms_template,
        }
        return await assign_client_template_repo.create(data)

    return assign_client_template


@fixture(scope="function")
async def assign_client_template(
    faker,
    city,
    sms_template,
    assign_client_template_repo,
):
    data = {
        "title": faker.text(max_nb_chars=20),
        "name": faker.word(),
        "text": faker.text(max_nb_chars=20),
        "success_assign_text": faker.text(max_nb_chars=20),
        "success_unassign_text": faker.text(max_nb_chars=20),
        "default": False,
        "city_id": city.id,
        "sms_id": sms_template.id,
    }
    template = await assign_client_template_repo.create(data)
    return template
