from collections import OrderedDict


class HistoryManagerProcessor:
    __history = {"last_uuid": None, "current_uuid": None}

    @property
    def last_uuid(self):
        return self.__history.get('last_uuid')

    @property
    def current_uuid(self):
        return self.__history.get('current_uuid')

    @property
    def uuid_changed(self):
        return self.last_uuid != self.current_uuid

    def __call__(self, logger, log_method, event_dict: dict) -> dict:
        self.__history['last_uuid'] = self.__history.get('current_uuid')
        self.__history['current_uuid'] = event_dict.get('request_id')
        return event_dict


class DelimiterProcessor:
    def __init__(self):
        self.history_manager: HistoryManagerProcessor = HistoryManagerProcessor()

    def __call__(self, logger, log_method, event_string: str) -> str:
        if self.history_manager.uuid_changed or 'exception' in event_string:
            event_string = f'{"=" * 60}\n{event_string}'
        return event_string


class SortKeysProcessor:
    def __init__(self, keys: list = None):
        self.keys = keys

    def __call__(self, logger, log_method, event_dict: dict) -> OrderedDict:
        if self.keys:
            sorted_dict = sorted(event_dict.items(),
                                 key=lambda key_val: self.keys.index(key_val[0])
                                 if key_val[0] in self.keys
                                 else float('inf'))
            event_dict = OrderedDict(sorted_dict)
        return event_dict

