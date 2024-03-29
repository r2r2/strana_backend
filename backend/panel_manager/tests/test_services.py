import factory
from django.db.models.signals import post_save
from rest_framework.response import Response
from rest_framework.test import APITestCase
from django.urls import reverse

from panel_manager.models import Meeting
from panel_manager.tests.factories import MeetingFactory

CREATE_UPDATE_METTING = {
    "sensei_hash": "21189697.83857170.6714a3cc3a1bd429.1637663614",
    "leads[sensei][0][id]": "28989810",
    "leads[sensei][0][date_create]": "1636708664",
    "leads[sensei][0][created_user_id]": "0",
    "leads[sensei][0][last_modified]": "1637663613",
    "leads[sensei][0][modified_user_id]": "0",
    "leads[sensei][0][name]": "Заявка с посадочной страницы +7 (932) 420-81-09",
    "leads[sensei][0][responsible_user_id]": "2760391",
    "leads[sensei][0][closest_task]": "0",
    "leads[sensei][0][tags][0][id]": "551919",
    "leads[sensei][0][tags][0][name]": "Заявка с сайта",
    "leads[sensei][0][tags][0][entity_type]": "2",
    "leads[sensei][0][tags][1][id]": "691621",
    "leads[sensei][0][tags][1][name]": "клиент",
    "leads[sensei][0][tags][1][entity_type]": "2",
    "leads[sensei][0][custom_fields][692726][id]": "692726",
    "leads[sensei][0][custom_fields][692726][name]": "Город",
    "leads[sensei][0][custom_fields][692726][type_id]": "4",
    "leads[sensei][0][custom_fields][692726][values][0][value]": "Тюмень",
    "leads[sensei][0][custom_fields][692726][values][0][enum]": "1322598",
    "leads[sensei][0][custom_fields][596489][id]": "596489",
    "leads[sensei][0][custom_fields][596489][name]": "Объект",
    "leads[sensei][0][custom_fields][596489][type_id]": "4",
    "leads[sensei][0][custom_fields][596489][values][0][value]": "Европейский берег",
    "leads[sensei][0][custom_fields][596489][values][0][enum]": "1173629",
    "leads[sensei][0][custom_fields][640865][id]": "640865",
    "leads[sensei][0][custom_fields][640865][name]": "UTM_source",
    "leads[sensei][0][custom_fields][640865][type_id]": "1",
    "leads[sensei][0][custom_fields][640865][values][0][value]": "yandex",
    "leads[sensei][0][custom_fields][640867][id]": "640867",
    "leads[sensei][0][custom_fields][640867][name]": "UTM_medium",
    "leads[sensei][0][custom_fields][640867][type_id]": "1",
    "leads[sensei][0][custom_fields][640867][values][0][value]": "cpc",
    "leads[sensei][0][custom_fields][640877][id]": "640877",
    "leads[sensei][0][custom_fields][640877][name]": "UTM_campaign",
    "leads[sensei][0][custom_fields][640877][type_id]": "1",
    "leads[sensei][0][custom_fields][640877][values][0][value]": "eurobereg-quiz-q32.khmao.d-m.rsya",
    "leads[sensei][0][custom_fields][640873][id]": "640873",
    "leads[sensei][0][custom_fields][640873][name]": "UTM_term",
    "leads[sensei][0][custom_fields][640873][type_id]": "1",
    "leads[sensei][0][custom_fields][640873][values][0][value]": "жк от застройщика тюмень",
    "leads[sensei][0][custom_fields][640871][id]": "640871",
    "leads[sensei][0][custom_fields][640871][name]": "UTM_content",
    "leads[sensei][0][custom_fields][640871][type_id]": "1",
    "leads[sensei][0][custom_fields][640871][values][0][value]": "4631481340",
    "leads[sensei][0][custom_fields][640853][id]": "640853",
    "leads[sensei][0][custom_fields][640853][name]": "Google Client ID",
    "leads[sensei][0][custom_fields][640853][type_id]": "1",
    "leads[sensei][0][custom_fields][640853][values][0][value]": "932532976.1636708638",
    "leads[sensei][0][custom_fields][694350][id]": "694350",
    "leads[sensei][0][custom_fields][694350][name]": "Yandex Client ID",
    "leads[sensei][0][custom_fields][694350][type_id]": "1",
    "leads[sensei][0][custom_fields][694350][values][0][value]": "1636708641702511909",
    "leads[sensei][0][custom_fields][677717][id]": "677717",
    "leads[sensei][0][custom_fields][677717][name]": "Источник лида",
    "leads[sensei][0][custom_fields][677717][type_id]": "4",
    "leads[sensei][0][custom_fields][677717][values][0][value]": "Контекстная реклама",
    "leads[sensei][0][custom_fields][677717][values][0][enum]": "1324384",
    "leads[sensei][0][custom_fields][641685][id]": "641685",
    "leads[sensei][0][custom_fields][641685][name]": "Организация",
    "leads[sensei][0][custom_fields][641685][type_id]": "4",
    "leads[sensei][0][custom_fields][641685][values][0][value]": "К2",
    "leads[sensei][0][custom_fields][641685][values][0][enum]": "1253331",
    "leads[sensei][0][custom_fields][676461][id]": "676461",
    "leads[sensei][0][custom_fields][676461][name]": "Имя контакта",
    "leads[sensei][0][custom_fields][676461][type_id]": "1",
    "leads[sensei][0][custom_fields][676461][values][0][value]": "Саид",
    "leads[sensei][0][custom_fields][366965][id]": "366965",
    "leads[sensei][0][custom_fields][366965][name]": "Тип помещения",
    "leads[sensei][0][custom_fields][366965][type_id]": "4",
    "leads[sensei][0][custom_fields][366965][values][0][value]": "Квартира",
    "leads[sensei][0][custom_fields][366965][values][0][enum]": "715523",
    "leads[sensei][0][custom_fields][694316][id]": "694316",
    "leads[sensei][0][custom_fields][694316][name]": "Тип следующего контакта",
    "leads[sensei][0][custom_fields][694316][type_id]": "4",
    "leads[sensei][0][custom_fields][694316][values][0][value]": "Видеоконференция",
    "leads[sensei][0][custom_fields][694316][values][0][enum]": "1323780",
    "leads[sensei][0][custom_fields][694314][id]": "694314",
    "leads[sensei][0][custom_fields][694314][name]": "Дата и время следующего контакта",
    "leads[sensei][0][custom_fields][694314][type_id]": "19",
    "leads[sensei][0][custom_fields][694314][values][0][value]": "2021-11-12 15:00:00",
    "leads[sensei][0][custom_fields][688595][id]": "688595",
    "leads[sensei][0][custom_fields][688595][name]": "Заявка на Zoom?",
    "leads[sensei][0][custom_fsenseiields][688595][type_id]": "1",
    "leads[sensei][0][custom_fields][688595][values][0][value]": "Да",
    "leads[sensei][0][custom_fields][688593][id]": "688593",
    "leads[sensei][0][custom_fields][688593][name]": "Дата и время Zoom",
    "leads[sensei][0][custom_fields][688593][type_id]": "19",
    "leads[sensei][0][custom_fields][688593][values][0][value]": "2021-11-12 15:00:00",
    "leads[sensei][0][custom_fields][682225][id]": "682225",
    "leads[sensei][0][custom_fields][682225][name]": "Менеджер колл-центра",
    "leads[sensei][0][custom_fields][682225][type_id]": "1",
    "leads[sensei][0][custom_fields][682225][values][0][value]": "Тюменцева Ксения Евгеньевна",
    "leads[sensei][0][custom_fields][815568][id]": "815568",
    "leads[sensei][0][custom_fields][815568][name]": "Тип встречи",
    "leads[sensei][0][custom_fields][815568][type_id]": "4",
    "leads[sensei][0][custom_fields][815568][values][0][value]": "В офисе",
    "leads[sensei][0][custom_fields][815568][values][0][enum]": "1326774",
    "leads[sensei][0][custom_fields][689581][id]": "689581",
    "leads[sensei][0][custom_fields][689581][name]": "Дата и время по Сенсей",
    "leads[sensei][0][custom_fields][689581][type_id]": "19",
    "leads[sensei][0][custom_fields][689581][values][0][value]": "2021-11-23 15:00:00",
    "leads[sensei][0][custom_fields][694394][id]": "694394",
    "leads[sensei][0][custom_fields][694394][name]": "ДКТ: ya_client_id",
    "leads[sensei][0][custom_fields][694394][type_id]": "1",
    "leads[sensei][0][custom_fields][694394][values][0][value]": "1636708641702511909",
    "leads[sensei][0][custom_fields][694398][id]": "694398",
    "leads[sensei][0][custom_fields][694398][name]": "ДКТ: Источник",
    "leads[sensei][0][custom_fields][694398][type_id]": "1",
    "leads[sensei][0][custom_fields][694398][values][0][value]": "yandex",
    "leads[sensei][0][custom_fields][694400][id]": "694400",
    "leads[sensei][0][custom_fields][694400][name]": "ДКТ: Канал",
    "leads[sensei][0][custom_fields][694400][type_id]": "1",
    "leads[sensei][0][custom_fields][694400][values][0][value]": "cpc",
    "leads[sensei][0][custom_fields][694402][id]": "694402",
    "leads[sensei][0][custom_fields][694402][name]": "ДКТ: Кампания",
    "leads[sensei][0][custom_fields][694402][type_id]": "1",
    "leads[sensei][0][custom_fields][694402][values][0][value]": "eurobereg-quiz-q32.khmao.d-m.rsya",
    "leads[sensei][0][custom_fields][694416][id]": "694416",
    "leads[sensei][0][custom_fields][694416][name]": "ДКТ: Страница звонка",
    "leads[sensei][0][custom_fields][694416][type_id]": "1",
    "leads[sensei][0][custom_fields][694416][values][0][value]": "https://strana-eurobereg.com/eurobereg72-kvartiry-v-centre-tyumeni-q32-spasibo",
    "leads[sensei][0][custom_fields][815646][id]": "815646",
    "leads[sensei][0][custom_fields][815646][name]": "Обновлена Calltouch",
    "leads[sensei][0][custom_fields][815646][type_id]": "1",
    "leads[sensei][0][custom_fields][815646][values][0][value]": "2021-11-22 13:36",
    "leads[sensei][0][custom_fields][630093][id]": "630093",
    "leads[sensei][0][custom_fields][630093][name]": "Встреча состоялась?",
    "leads[sensei][0][custom_fields][630093][type_id]": "4",
    "leads[sensei][0][custom_fields][630093][values][0][value]": "Нет",
    "leads[sensei][0][custom_fields][630093][values][0][enum]": "1233403",
    "leads[sensei][0][custom_fields][815570][id]": "815570",
    "leads[sensei][0][custom_fields][815570][name]": "Какие ЖК рассматривает",
    "leads[sensei][0][custom_fields][815570][type_id]": "5",
    "leads[sensei][0][custom_fields][815570][values][0][value]": "Европейский берег",
    "leads[sensei][0][custom_fields][815570][values][0][enum]": "1326784",
    "leads[sensei][0][custom_fields][548137][id]": "548137",
    "leads[sensei][0][custom_fields][548137][name]": "Сколько ком.кв. хочет купить?",
    "leads[sensei][0][custom_fields][548137][type_id]": "5",
    "leads[sensei][0][custom_fields][548137][values][0][value]": "Euro 3-ком.",
    "leads[sensei][0][custom_fields][548137][values][0][enum]": "1217243",
    "leads[sensei][0][custom_fields][366639][id]": "366639",
    "leads[sensei][0][custom_fields][366639][name]": "Тип оплаты",
    "leads[sensei][0][custom_fields][366639][type_id]": "4",
    "leads[sensei][0][custom_fields][366639][values][0][value]": "Ипотека",
    "leads[sensei][0][custom_fields][366639][values][0][enum]": "714855",
    "leads[sensei][0][custom_fields][688723][id]": "688723",
    "leads[sensei][0][custom_fields][688723][name]": "Ипотека одобрена?",
    "leads[sensei][0][custom_fields][688723][type_id]": "4",
    "leads[sensei][0][custom_fields][688723][values][0][value]": "нет",
    "leads[sensei][0][custom_fields][688723][values][0][enum]": "1317491",
    "leads[sensei][0][custom_fields][691100][id]": "691100",
    "leads[sensei][0][custom_fields][691100][name]": "Видеоконференция",
    "leads[sensei][0][custom_fields][691100][type_id]": "1",
    "leads[sensei][0][custom_fields][691100][values][0][value]": "02:11:34",
    "leads[sensei][0][custom_fields][691718][id]": "691718",
    "leads[sensei][0][custom_fields][691718][name]": "Лид?",
    "leads[sensei][0][custom_fields][691718][type_id]": "4",
    "leads[sensei][0][custom_fields][691718][values][0][value]": "Лид",
    "leads[sensei][0][custom_fields][691718][values][0][enum]": "1321730",
    "leads[sensei][0][custom_fields][693088][id]": "693088",
    "leads[sensei][0][custom_fields][693088][name]": "Дата лида",
    "leads[sensei][0][custom_fields][693088][type_id]": "19",
    "leads[sensei][0][custom_fields][693088][values][0][value]": "2021-11-12 00:00:00",
    "leads[sensei][0][custom_fields][691786][id]": "691786",
    "leads[sensei][0][custom_fields][691786][name]": "Отказ от встречи",
    "leads[sensei][0][custom_fields][691786][type_id]": "4",
    "leads[sensei][0][custom_fields][691786][values][0][value]": "передумали покупать",
    "leads[sensei][0][custom_fields][691786][values][0][enum]": "1321884",
    "leads[sensei][0][date_close]": "0",
    "leads[sensei][0][pipeline_id]": "1305043",
    "leads[sensei][0][status_id]": "36204951",
    "leads[sensei][0][price]": "0",
    "contacts[sensei][0][id]": "48582474",
    "contacts[sensei][0][type]": "contact",
    "contacts[sensei][0][date_create]": "1636708665",
    "contacts[sensei][0][created_user_id]": "0",
    "contacts[sensei][0][last_modified]": "1637663613",
    "contacts[sensei][0][modified_user_id]": "0",
    "contacts[sensei][0][name]": "Саид",
    "contacts[sensei][0][responsible_user_id]": "2760391",
    "contacts[sensei][0][closest_task]": "0",
    "contacts[sensei][0][tags][0][id]": "555355",
    "contacts[sensei][0][tags][0][name]": "клиент",
    "contacts[sensei][0][tags][0][entity_type]": "1",
    "contacts[sensei][0][custom_fields][362093][id]": "362093",
    "contacts[sensei][0][custom_fields][362093][name]": "Телефон",
    "contacts[sensei][0][custom_fields][362093][type_id]": "8",
    "contacts[sensei][0][custom_fields][362093][code]": "PHONE",
    "contacts[sensei][0][custom_fields][362093][values][0][value]": "+79324208109",
    "contacts[sensei][0][custom_fields][362093][values][0][enum]": "706653",
    "contacts[sensei][0][custom_fields][812842][id]": "812842",
    "contacts[sensei][0][custom_fields][812842][name]": "Место проживания",
    "contacts[sensei][0][custom_fields][812842][type_id]": "1",
    "contacts[sensei][0][custom_fields][812842][values][0][value]": "Север",
    "contacts[sensei][0][company_name]": "",
    "id": "28989810",
}


class TestServicesViewset(APITestCase):
    def test_update_or_create_meeting_from_webhook_wrong_status(self):
        data = CREATE_UPDATE_METTING.copy()
        data["leads[sensei][0][status_id]"] = "36204952"
        response: Response = self.client.post("/api/panel/web_hook_meeting/", data=data)
        assert response.status_code == 400

    @factory.django.mute_signals(post_save)
    def test_update_or_create_meeting_from_webhook(self):
        response: Response = self.client.post(
            "/api/panel/web_hook_meeting/", data=CREATE_UPDATE_METTING
        )
        assert response.status_code == 200
        meetings: Meeting = Meeting.objects.first()
        self.assertIsNotNone(meetings)
        self.assertEqual(meetings.id_crm, CREATE_UPDATE_METTING["leads[sensei][0][id]"])

    @factory.django.mute_signals(post_save)
    def test_deactivate_from_webhook(self):
        MeetingFactory(id_crm="1234")
        data = CREATE_UPDATE_METTING.copy()
        data["id"] = "1234"
        data["leads[sensei][0][id]"] = "1234"
        data["happened"] = "Нет"
        response: Response = self.client.post("/api/panel/web_hook_meeting/", data=data)
        assert response.status_code == 200
        meetings: Meeting = Meeting.objects.first()
        self.assertIsNotNone(meetings)
        self.assertEqual(meetings.id_crm, data["leads[sensei][0][id]"])
        self.assertEqual(meetings.active, False)
