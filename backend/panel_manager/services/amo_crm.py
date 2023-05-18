import datetime
from collections import namedtuple
from logging import getLogger

import dateutil
from django.contrib.sites.models import Site
from django.db.models import Q
from django.utils.timezone import now
from requests import RequestException

from amocrm.services import AmoCRM
from cities.models import City
from panel_manager.const import (MeetingEndTypeChoices, NextMeetingTypeChoices,
                                 RoomsChoices)
from panel_manager.models import Client, Manager, Meeting, MeetingDetails
from profitbase.api import ProfitBaseAPI
from projects.models import Project

logger = getLogger(__name__)
State = namedtuple('State', 'state_id, city_id')
# 1305043 - Тюмень 3568449 - CПб, 1941865 - Москва, ЕКБ 5798376
# Входящий поток 3934218
STATES = {
    21189706: State(MeetingEndTypeChoices.APPOINTED, 1305043),
    21189709: State(MeetingEndTypeChoices.IN_PROGRESS, 1305043),
    21189712: State(MeetingEndTypeChoices.DECIDE, 1305043),
    40850076: State(MeetingEndTypeChoices.REPEAT, 1305043),
    21197641: State(MeetingEndTypeChoices.BOOKING, 1305043),

    36204951: State(MeetingEndTypeChoices.APPOINTED, 3568449),
    41182452: State(MeetingEndTypeChoices.IN_PROGRESS, 3568449),
    36204954: State(MeetingEndTypeChoices.DECIDE, 3568449),
    41182443: State(MeetingEndTypeChoices.REPEAT, 3568449),
    35065584: State(MeetingEndTypeChoices.BOOKING, 3568449),

    45598248: State(MeetingEndTypeChoices.APPOINTED, 1941865),
    45598251: State(MeetingEndTypeChoices.IN_PROGRESS, 1941865),
    29096398: State(MeetingEndTypeChoices.DECIDE, 1941865),
    45598254: State(MeetingEndTypeChoices.REPEAT, 1941865),
    29096401: State(MeetingEndTypeChoices.BOOKING, 1941865),

    50814930: State(MeetingEndTypeChoices.APPOINTED, 5798376),
    50814843: State(MeetingEndTypeChoices.IN_PROGRESS, 5798376),
    50814933: State(MeetingEndTypeChoices.DECIDE, 5798376),
    50814936: State(MeetingEndTypeChoices.REPEAT, 5798376),
    50814939: State(MeetingEndTypeChoices.BOOKING, 5798376),
    143: State(MeetingEndTypeChoices.CANCEL, None)
}


class PanelManagerAmoCrm(AmoCRM):
    """Сервис для работы с заявками с панели менеджера."""
    STATUS_ID = {}
    for status_id, state in STATES.items():
        state: State
        if state.city_id not in STATUS_ID.keys():
            STATUS_ID.update({state.city_id: {}})
        STATUS_ID[state.city_id][state.state_id] = status_id

    @staticmethod
    def deactivate_meeting(id_crm: str):
        """Деактивация встречи"""
        Meeting.objects.filter(id_crm=id_crm).update(active=False)

    def processing_webhook(self, data, site_id = None):
        """Обработка данных с webhook"""
        if data.get("happened", "") == "Нет":  # деактивация встречи
            self.deactivate_meeting(data.get("id"))
        else:  # создание встречи
            self.update_or_create_meeting_from_webhook(data, site_id = None)

    @staticmethod
    def _process_closed_meeting(data: dict):
        """Закрытие встречи по причине отказа."""
        update_dict = {
            "meeting_end_type": MeetingEndTypeChoices.CANCEL,
            "active": False,
            "comment": f"Причины отказа: {data.get('leads[sensei][0][custom_fields][694446][values][0][value]')}"
        }
        Meeting.objects.filter(id_crm=data.get("leads[sensei][0][id]")).update(**update_dict)

    def update_or_create_meeting_from_webhook(self, data: dict, site_id = None):
        """Создание или обновление встречи от CRM"""
        status = data.get("leads[sensei][0][status_id]", 0)
        if int(status) == 143:
            return self._process_closed_meeting(data)
        if int(status) not in STATES.keys():
            logger.error(f"Неизвестный статус сделки: {status}")
            return
        ids = data.get("leads[sensei][0][id]")
        # Create client
        client_name = data.get("contacts[sensei][0][name]")
        client_id = data.get("contacts[sensei][0][id]")
        client_phone = data.get("contacts[sensei][0][custom_fields][362093][values][0][value]")
        client_email = data.get("contacts[sensei][0][custom_fields][362095][values][0][value]")
        client, _ = Client.objects.update_or_create(
            id_crm=client_id, defaults={"name": client_name, "phone": client_phone, "email": client_email}
        )
        # Project
        project_enum = data.get("leads[sensei][0][custom_fields][596489][values][0][enum]")
        project_name = data.get("leads[sensei][0][custom_fields][596489][values][0][value]")
        project = Project.objects.filter(Q(amocrm_enum=project_enum) | Q(name=project_name)).first()
        city_name = data.get("leads[sensei][0][custom_fields][692726][values][0][value]")
        city_enum = data.get("leads[sensei][0][custom_fields][692726][values][0][enum]")
        city, _ = City.objects.get_or_create(amocrm_enum=city_enum, defaults={
            "site_id": site_id,
            "name": city_name
        })

        # Перечень полей, в которых может содержаться дата/время начала встречи
        start_time_fields = [
            "datetime",
            "leads[sensei][0][custom_fields][694314][values][0][value]",
            "leads[sensei][0][custom_fields][689581][values][0][value]"
        ]
        start_date = None
        for field in start_time_fields:
            if data.get(field):
                start_date = data[field]
                break
        update_dict = {"client_id": str(client.id), "project": project}
        manager_fio = data.get("process_params[global][8091][value]", "").replace("/n", "").strip().split(" ")
        if manager := Manager.objects.filter(user__last_name=manager_fio[0]).last():
            update_dict["manager_id"] = manager.id
        if start_date:
            try:
                update_dict["datetime_start"] = datetime.datetime.strptime(
                    start_date, "%d.%m.%Y %H:%M"
                )
            except ValueError:
                update_dict["datetime_start"] = dateutil.parser.parse(start_date)
            finally:
                update_dict["datetime_start"] -= datetime.timedelta(hours=2)
        else:
            update_dict["datetime_start"] = datetime.datetime.now() + datetime.timedelta(hours=3)

        # Поиск брокера
        key_agent_name = ""
        key_agent_fio = ""
        for key, value in data.items():
            if str(value) == "437407":
                number_tag = key.replace("contacts[sensei][", "").replace("][tags][0][id]", "")
                key_agent_name = data.get(f"contacts[sensei][{number_tag}][company_name]", "")
                key_agent_fio = data.get(f"contacts[sensei][{number_tag}][name]", "")
        update_dict.update({
            "agent_company": key_agent_name,
            "agent_fio": key_agent_fio,
            "meeting_end_type": STATES[int(status)].state_id,
            "city_id": city.id
        })
        meeting, created = Meeting.objects.get_or_create(id_crm=ids, defaults=update_dict)
        details, _ = MeetingDetails.objects.get_or_create(meeting=meeting)
        if not created:
            Meeting.objects.filter(id=meeting.id).update(**update_dict)

    def update_meeting_in_crm(self, meeting: Meeting = None):
        """Обновление встречи в CRM"""
        lead = self.get_lead(meeting.id_crm)
        if not lead:
            logger.debug("Нет данных о встрече в AmoCRM.")
            return
        custom_fields = []

        tag_names = ["Заявка с сайта", "Панель менеджера"]
        if lead.get("tags"):
            old_tag_names = [tag["name"] for tag in lead["tags"]]
            tag_names = set(tag_names + old_tag_names)
        tag_names = ",".join(tag_names)

        custom_fields.append(
            {"id": 366965, "values": [{"value": "715523"}]}
        )  # Тип помещения - Квартира
        pipeline_id = lead.get('pipeline_id')
        if meeting.project:  # Проект\Объект
            custom_fields.append({"id": 596489, "values": [{"value": meeting.project.amocrm_enum}]})

        if meeting.next_meeting_type:
            custom_fields.append({"id": 694316, "values": [{"value": meeting.next_meeting_type}]})
            if meeting.next_meeting_type == NextMeetingTypeChoices.MEETING:
                custom_fields.append(
                    {
                        "id": 694314,
                        "values": [
                            {"value": int((now() + datetime.timedelta(days=3)).timestamp())}
                        ],
                    }
                )
                custom_fields.append(
                    {
                        "id": 689581,
                        "values": [
                            {"value": int((now() + datetime.timedelta(days=3)).timestamp())}
                        ],
                    }
                )
            else:
                custom_fields.append(
                    {
                        "id": 694314,
                        "values": [{"value": int(meeting.next_meeting_datetime.timestamp())}],
                    }
                )
        if meeting.form_pay:
            custom_fields.append({"id": 366639, "values": [{"value": meeting.form_pay}]})
        if meeting.money:
            custom_fields.append({"id": 829092, "values": [{"value": meeting.money}]})
        if meeting.mortgage_approved:
            custom_fields.append(
                {
                    "id": 688723,
                    "values": [
                        {"value": 1317489} if meeting.mortgage_approved else {"value": 1317491}
                    ],
                }
            )
        if meeting.rooms:
            rooms = [{"value": RoomsChoices(i).name, "enum": i} for i in meeting.rooms]
            custom_fields.append({"id": 548137, "values": rooms})
        notes = list()
        if favorited := meeting.favorite_property.all():
            t = ', '.join(str(favorite) for favorite in favorited)
            notes.append('Избранные помещения: ' + t)
        booltostr = {
            True: "да", False: "нет"
        }
        if hasattr(meeting, "details"):
            notes.extend([
                "Способ покупки: " + meeting.get_form_pay_display(),
                "Срок покупки: " + str(meeting.purchase_term) if meeting.purchase_term else "--",
                f"Итоговая сумма ипотеки: {meeting.details.total_mortgage_amount}",
                "Первоначальный взнос: " + str(meeting.details.initial_payment),
                "Наличие одобрения в других банках: " + booltostr[meeting.details.has_other_approvals]
            ])
        if meeting.booked_property:
            custom_fields.append({"id": 363971, "values": [{"value": meeting.booked_property_id}]})
            custom_fields.append(
                {
                    "id": 643041,
                    "values": [{"value": int(now().timestamp())}],
                }
            )
            custom_fields.append(
                {
                    "id": 689005,
                    "values": [{"value": int(now().timestamp())}],
                }
            )
            custom_fields.append(
                {
                    "id": 643043,
                    "values": [{"value": int((now() + datetime.timedelta(days=3)).timestamp())}],
                }
            )
            ProfitBaseAPI().property_booking(
                id_property=str(meeting.booked_property_id), deal_id=str(meeting.id_crm)
            )

        update_data = {
            "id": meeting.id_crm,
            "updated_at": int(now().timestamp()),
            "tags": tag_names,
            "custom_fields": custom_fields
        }
        if meeting.meeting_end_type and pipeline_id:
            status = self.STATUS_ID.get(pipeline_id, {}).get(meeting.meeting_end_type, None)
            if status:
                update_data["status_id"] = status
                update_data["pipeline_id"] = pipeline_id
        data = {"update": [update_data]}
        client_id = lead["contacts"]["id"][0] if "contacts" in lead.keys() else meeting.client.id_crm
        client_data = {
            "id": client_id,
            "custom_fields_values": [
                {"field_id": 362095, "values": [
                    {"enum_code": "WORK", "value": meeting.client.email}
                ]}
            ]
        }
        self.create_note(meeting.id_crm, "\n".join(notes))
        try:
            self.request_patch_v4("contacts", [client_data])
        except RequestException as e:
            logger.error(f'Не удалось обновить данные о клиенте: {e}')
        res = self.request_post("leads", data)
        return res.json()["_embedded"]["items"][0]["id"]

    def create_update_tasks(self, meeting: Meeting):
        task_json = self.get_tasks("tasks", f"filter[entity_id][]={meeting.id_crm}&limit=10")
        if task_json:
            tasks = task_json["_embedded"]["tasks"]
            for t in tasks:
                if t["text"] == "Перевести сделку по результату встречи":
                    task_id = t["id"]
                    if meeting.meeting_end_type == MeetingEndTypeChoices.DECIDE:
                        # закрыть задачу «Перевести сделку по результату встречи» в сделке с результатом «принимает решение»
                        response = self.close_task(
                            task_id,
                            {
                                "result": {"text": MeetingEndTypeChoices.DECIDE.label},
                                "is_completed": True,
                            },
                        )
                    if meeting.meeting_end_type == MeetingEndTypeChoices.BOOKING:
                        # закрыть задачу «Перевести сделку по результату встречи» в сделке с результатом Бронь
                        response = self.close_task(
                            task_id,
                            {
                                "result": {"text": MeetingEndTypeChoices.BOOKING.label},
                                "is_completed": True,
                            },
                        )

                    elif meeting.meeting_end_type == MeetingEndTypeChoices.REPEAT:
                        # закрыть задачу «Перевести сделку по результату встречи» в сделке с результатом «Повторная встреча»
                        response = self.close_task(
                            task_id,
                            {
                                "result": {"text": MeetingEndTypeChoices.DECIDE.label},
                                "is_completed": True,
                            },
                        )
                    elif meeting.meeting_end_type == MeetingEndTypeChoices.CANCEL:
                        # закрыть задачу «Перевести сделку по результату встречи» в сделке с результатом «Отказ»
                        response = self.close_task(
                            task_id,
                            {
                                "result": {"text": MeetingEndTypeChoices.CANCEL.label},
                                "is_completed": True,
                            },
                        )

    def close_task(self, ids: str, data: {}):
        res = self.request_patch_v4(f"tasks/{ids}", data=data)
        return res.json()
