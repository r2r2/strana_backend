from datetime import datetime

from ..entities import BaseNotificationCase
from ..repos import OnboardingUserThroughRepo


class ReadOnboardingCase(BaseNotificationCase):
    """
    Прочтение уведомления онбординга
    """

    def __init__(
            self,
            onboarding_through_repo: type[OnboardingUserThroughRepo],
    ):
        self.onboarding_through_repo = onboarding_through_repo()

    async def __call__(self, user_id: int, onboarding_id: int):
        filters = dict(
            user_id=user_id,
            onboarding_id=onboarding_id,
        )
        user_onboarding = await self.onboarding_through_repo.retrieve(filters=filters)
        data = dict(
            is_read=True,
            read=datetime.utcnow(),
        )
        await self.onboarding_through_repo.update(model=user_onboarding, data=data)
