class QueryStorage(dict):

    def add(self, query_name, options):
        self[query_name] = options

    @property
    def queries(self) -> list:
        return list(self.keys())


query_storage = QueryStorage()
