from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.push_notifications import PushClientCredentials
from src.modules.storage.interface.push_notifications import PushNotificationConfigsOperationsProtocol
from src.modules.storage.models import PushNotificationConfig
from src.providers.time import datetime_now


class PushNotificationConfigsOperations(PushNotificationConfigsOperationsProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_config(
        self,
        user_id: int,
        device_id: str,
        credentials: PushClientCredentials,
    ) -> PushNotificationConfig | None:
        dt_now = datetime_now()
        cfg = PushNotificationConfig(
            created_at=dt_now,
            user_id=user_id,
            endpoint=credentials.endpoint,
            keys=credentials.keys,
            device_id=device_id,
            last_alive_at=dt_now,
        )
        self.session.add(cfg)
        try:
            await self.session.flush(objects=[cfg])
            return cfg
        except IntegrityError:
            return None

    async def get_and_mark_as_alive(self, device_id: str) -> PushNotificationConfig | None:
        query = (
            update(PushNotificationConfig)
            .values(last_alive_at=datetime_now())
            .where(PushNotificationConfig.device_id == device_id)
            .returning(PushNotificationConfig)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def remove_configs(self, device_id: str) -> bool:
        query = (
            delete(PushNotificationConfig)
            .where(PushNotificationConfig.device_id == device_id)
            .returning(PushNotificationConfig.id)
        )
        result = await self.session.execute(query)
        return bool(result.scalars().first())

    async def get_configs_for_user(self, user_id: int) -> list[PushNotificationConfig]:
        query = select(PushNotificationConfig).where(PushNotificationConfig.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def invalidate_configs(self, user_id: int) -> None:
        query = delete(PushNotificationConfig).where(PushNotificationConfig.user_id == user_id)
        await self.session.execute(query)

    async def get_config_by_endpoint(self, endpoint: str, user_id: int) -> PushNotificationConfig | None:
        query = select(PushNotificationConfig).where(
            PushNotificationConfig.endpoint == endpoint, PushNotificationConfig.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
