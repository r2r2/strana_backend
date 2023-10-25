from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from ..entities import BaseFeatureFlagCase
from icecream import ic


class GetFeatureFlagsCase(BaseFeatureFlagCase):
    def __init__(self, unleash: UnleashClient):
        self.unleash = unleash

    async def __call__(
        self,
        feature_flags: list[str],
        user_id: int | None,
    ):
        ic(feature_flags)
        feature_flags_enabled: dict[str, bool] = {}
        for feature_flag in feature_flags:
            try:
                feature_flags_enabled[feature_flag] = self.unleash.is_enabled(
                    FeatureFlags(feature_flag), context=dict(userId=user_id),
                )
            except Exception:
                feature_flags_enabled[feature_flag] = False
        return feature_flags_enabled
