import uuid
from typing import Callable
from UnleashClient import UnleashClient, Feature, UnleashEvent, UnleashEventType
from UnleashClient.utils import LOGGER
from UnleashClient.loader import load_features


class UnleashAdapter(UnleashClient):
    def is_enabled(
        self,
        feature_name: str,
        context: dict | None = None,
        fallback_function: Callable = None,
    ) -> bool:
        """
        Checks if a feature toggle is enabled.

        Notes:

        * If client hasn't been initialized yet or an error occurs, flat will default to false.

        :param feature_name: Name of the feature
        :param context: Dictionary with context (e.g. IPs, email) for feature toggle.
        :param fallback_function: Allows users to provide a custom function to set default value.
        :return: Feature flag result
        """
        context = context or {}

        base_context = self.unleash_static_context.copy()
        # Update context with static values and allow context to override environment
        base_context.update(context)
        context = base_context

        if self.unleash_bootstrapped or self.is_initialized:
            try:
                load_features(
                    cache=self.cache,
                    feature_toggles=self.features,
                    strategy_mapping=self.strategy_mapping,
                )
                feature = self.features[feature_name]
                feature_check = feature.is_enabled(context)

                if feature.only_for_metrics:
                    return self._get_fallback_value(
                        fallback_function, feature_name, context
                    )

                try:
                    if self.unleash_event_callback and feature.impression_data:
                        event = UnleashEvent(
                            event_type=UnleashEventType.FEATURE_FLAG,
                            event_id=uuid.uuid4(),
                            context=context,
                            enabled=feature_check,
                            feature_name=feature_name,
                        )

                        self.unleash_event_callback(event)
                except Exception as excep:
                    LOGGER.log(
                        self.unleash_verbose_log_level,
                        "Error in event callback: %s",
                        excep,
                    )
                    return feature_check

                return feature_check
            except Exception as excep:
                LOGGER.log(
                    self.unleash_verbose_log_level,
                    "Returning default value for feature: %s",
                    feature_name,
                )
                LOGGER.log(
                    self.unleash_verbose_log_level,
                    "Error checking feature flag: %s",
                    excep,
                )
                # The feature doesn't exist, so create it to track metrics
                new_feature = Feature.metrics_only_feature(feature_name)
                self.features[feature_name] = new_feature

                # Use the feature's is_enabled method to count the call
                new_feature.is_enabled(context)

                return self._get_fallback_value(
                    fallback_function, feature_name, context
                )

        else:
            LOGGER.log(
                self.unleash_verbose_log_level,
                "Returning default value for feature: %s",
                feature_name,
            )
            LOGGER.log(
                self.unleash_verbose_log_level,
                "Attempted to get feature_flag %s, but client wasn't initialized!",
                feature_name,
            )
            return self._get_fallback_value(fallback_function, feature_name, context)
