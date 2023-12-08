from fastapi import (
    APIRouter,
    Body,
    status,
)
from src.properties.services import (
    ImportPropertyService,
    ImportPropertyServiceFactory,
)
from common import amocrm, utils
from src.properties import repos as properties_repos
from src.booking import repos as booking_repos
from src.users import repos as users_repos
from src.commercial_offers import models
from src.commercial_offers import use_cases
from src.projects import repos as project_repos
from src.commercial_offers import repos as offer_repo


router = APIRouter(prefix="/offers", tags=["Коммерческие предложения"])


@router.post("/create_offer", status_code=status.HTTP_200_OK)
async def create_offer_view(
    payload: models.RequestCreateOfferModel = Body(...),
):
    """
    Создание коммерческого предложения
    """
    import_property_service: ImportPropertyService = (
        ImportPropertyServiceFactory.create()
    )

    resources: dict = dict(
        property_repo=properties_repos.PropertyRepo,
        property_type_repo=properties_repos.PropertyTypeRepo,
        booking_repo=booking_repos.BookingRepo,
        user_repo=users_repos.UserRepo,
        import_property_service=import_property_service,
        amocrm_class=amocrm.AmoCRM,
        global_id_decoder=utils.from_global_id,
        project_repo=project_repos.ProjectRepo,
        offer_repo=offer_repo.offer.OfferRepo,
        offer_source_repo=offer_repo.offer_source.OfferSourceRepo,
        offer_properties_repo=offer_repo.offer_property.OfferPropertyRepo,
    )

    create_offer: use_cases.CreateOfferCaseSaving = use_cases.CreateOfferCaseSaving(
        **resources
    )

    return await create_offer(payload=payload)
