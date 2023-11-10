from datetime import datetime

from ..entities import BaseNotificationCase
from ..repos import OnboardingRepo, OnboardingUserThroughRepo


class GetOnboardingListCase(BaseNotificationCase):
    """
    Получение списка уведомлений онбординга для пользователя
    В данной реализации важно что пользователь должен быть связан с уведомлением чтобы его получить
    """

    def __init__(
            self,
            onboarding_repo: type[OnboardingRepo],
            onboarding_through_repo: type[OnboardingUserThroughRepo],
    ):
        self.onboarding_repo = onboarding_repo()
        self.onboarding_through_repo = onboarding_through_repo()

    async def __call__(self, user_id: int):
        filters = dict(
            user=user_id,
            user_through__is_read=False,
        )
        onboarding_list = await self.onboarding_repo.list(filters=filters)

        filters = dict(
            user_id=user_id,
            onboarding_id__in=[onboarding.id for onboarding in onboarding_list]
        )
        data = dict(
            is_sent=True,
            sent=datetime.utcnow(),
        )
        await self.onboarding_through_repo.bulk_update(filters=filters, data=data)

        return onboarding_list
