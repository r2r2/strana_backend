from src.core.common.utility import PatternStrEnum


class UnreadCountCacheKey(PatternStrEnum):
    BY_CHAT = "[unread_counters]:[by_chat]:[user-{user_id}]:[chat-{chat_id}]"
    BY_MATCH = "[unread_counters]:[by_match]:[user-{user_id}]:[match-{match_id}]"
    BY_CHAT_TYPE = "[unread_counters]:[by_chat_type]:[user-{user_id}]:[chat_type-{chat_type}]"
    TOTAL = "[unread_counters]:[total]:[user-{user_id}]"


class RedisPubSubChannelName(PatternStrEnum):
    CONNECTION_UPDATES = "[user_updates]:[{connection_id}]"
    UNREAD_COUNTERS_UPDATES = "[unread_counters_updates]:[{user_id}]"
    USER_DATA_CACHE_INVALIDATION = "[user_cache_invalidation]"
