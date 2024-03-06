from common import amocrm, profitbase, utils, requests
from src.booking import repos as booking_repos
from src.booking import tasks
from src.booking.services import ActivateBookingService
from src.buildings import repos as buildings_repos
from src.notifications import tasks as notification_tasks
from src.properties import repos as properties_repos


class ActivateBookingServiceFactory:
    @staticmethod
    def create() -> ActivateBookingService:
        return ActivateBookingService(
            create_amocrm_log_task=tasks.create_amocrm_log_task,
            create_booking_log_task=tasks.create_booking_log_task,
            check_booking_task=tasks.check_booking_task,
            booking_repo=booking_repos.BookingRepo,
            amocrm_class=amocrm.AmoCRM,
            profitbase_class=profitbase.ProfitBase,
            global_id_decoder=utils.from_global_id,
            building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
            property_repo=properties_repos.PropertyRepo,
            request_class=requests.UpdateSqlRequest,
            booking_notification_sms_task=notification_tasks.booking_notification_sms_task,
            test_booking_repo=booking_repos.TestBookingRepo,
        )
