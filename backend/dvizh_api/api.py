from requests import post, exceptions as ex
from dvizh_api.models import DvizhApiSettings
from dvizh_api import queries, exceptions


class DvizhApiService:
    AUTH = "loanOfficer_SignIn"
    OFFERS = "getLoanOffer"
    COMPLEXES = "getHousingComplex"
    BANKS = "getHousingComplexBankByHousingComplexUuid"

    def __init__(self):
        self.settings = DvizhApiSettings.get_solo()
        self.headers = self._get_headers()

    def _get_headers(self) -> dict:
        token = self.settings.token
        return dict(Authorization=f"Bearer {token}")

    def auth(self):
        settings = self.settings
        settings.token = self._request(
            self.AUTH, dict(email=self.settings.user, password=self.settings.password)
        )
        settings.save()
        self.headers = self._get_headers()

    def _request(self, query_name: str, variables=None) -> dict:
        if variables is None:
            variables = {}
        try:
            query = getattr(queries, query_name).safe_substitute(**variables).strip()
            res = post(
                url=self.settings.endpoint,
                headers=self.headers,
                data=dict(query=query),
            )
            res.raise_for_status()
            data = res.json()
            if data.get("error"):
                if data["error"]["code"] == 401 and data["error"]["code"] == "Unauthorized":
                    raise exceptions.UserPasswordWrongDvizhException(**data["error"])
                if data["error"]["code"] == 401:
                    raise exceptions.TokenExpiredException(**data)
                raise exceptions.BaseDvizhException(**data["error"])
        except (exceptions.TokenExpiredException, ex.HTTPError) as e:
            if isinstance(e, ex.HTTPError) and e.response.status_code == 400:
                print(e.response)
                raise e
            self.auth()
            data = self._request(query_name=query_name, variables=variables)
        try:
            return data["data"][query_name]
        except KeyError:
            print(res)
            raise exceptions.BaseDvizhException(**data["error"][0])

    def get_offers(self, complex_id: int, agenda_type: str, mortgage_type: str, price:int):
        variables = dict(
            complex_id=complex_id, agenda_type=agenda_type, mortgage_type=mortgage_type, cost=price
        )
        res = self._request(self.OFFERS, variables=variables)
        return res

    def get_complexes(self):
        return self._request(self.COMPLEXES)["collection"]

    def get_banks_complex(self, complex_uuid: str):
        return self._request(self.BANKS, dict(uuid=complex_uuid))["collection"]
