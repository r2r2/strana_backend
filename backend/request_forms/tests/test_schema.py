import json
from unittest.mock import patch, Mock
from graphql_relay import to_global_id
from django.utils.timezone import now
from django.core.files.temp import NamedTemporaryFile

from cities.tests.factories import CityFactory
from common.test_cases import BaseTestCase
from contacts.schema import OfficeType
from contacts.tests.factories import OfficeFactory
from company.schemas.vacancy_schema import VacancyCategoryType
from properties.constants import PropertyType
from company.tests.factories import VacancyFactory, VacancyCategoryFactory
from projects.tests.factories import ProjectFactory
from properties.schema import FlatType
from properties.tests.factories import FlatFactory
from news.tests.factories import NewsFactory
from news.schema import NewsType
from landing.constants import LandingBlockChoices
from landing.tests.factories import LandingBlockFactory
from main_page.tests.factories import MainPageSlideFactory, MainPageFactory
from .factories import ManagerFactory, CustomFormFactory, CustomFormEmployeeFactory
from ..models import *


@patch("request_forms.services.send_mail", new_callable=Mock)
class SaleRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    saleRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                        cadastralNumber: "1111111111111"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["saleRequest"]["ok"], False)
        self.assertEqual(content["data"]["saleRequest"]["request"], None)
        self.assertEqual(len(content["data"]["saleRequest"]["errors"]), 2)
        self.assertEqual(content["data"]["saleRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()
        query = """
            mutation {
                saleRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    cadastralNumber: "1111111111111",
                    email: "test@gmail.com"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        with self.assertNumQueries(4):
            res = self.client.post(
                path=self.GRAPHQL_URL,
                data={"query": query, "documents": NamedTemporaryFile(suffix=".doc")},
            )
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["saleRequest"]["ok"], True)
        self.assertEqual(SaleRequest.objects.all().count(), 1)
        request = SaleRequest.objects.all().first()
        self.assertEqual(int(content["data"]["saleRequest"]["request"]["id"]), request.id)
        document = SaleRequestDocument.objects.filter(request=request).first()
        self.assertNotEqual(document, None)
        self.assertIsNone(content["data"]["saleRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class VacancyRequestTest(BaseTestCase):
    def test_with_wrong_vacancy(self, mock):
        query = """
                mutation {
                    vacancyRequest (input: {
                        vacancy: "123"
                        name: "Name"
                        phone: "+79999999999"
                        position: "dev"
                        city: "Москва"
                        graduatedAt: "2021-07-02"
                        specialty: "povar"
                        institution: "kitchen"
                    }) {
                        ok
                        request {
                            id
                        }
                          errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(1):
            res = self.client.post(
                path=self.GRAPHQL_URL,
                data={"query": query, "resume": NamedTemporaryFile(suffix=".doc")},
            )
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["vacancyRequest"]["ok"], False)
        self.assertEqual(content["data"]["vacancyRequest"]["request"], None)
        self.assertEqual(len(content["data"]["vacancyRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["vacancyRequest"]["errors"][0]["field"], "vacancy")
        mock.assert_not_called()

    def test_with_wrong_phone(self, mock):
        city = CityFactory()
        vacancy_category = VacancyCategoryFactory()
        vacancy = VacancyFactory(category=vacancy_category, city=city)
        vacancy_id = to_global_id(VacancyCategoryType.__name__, vacancy.id)

        query = (
            """
                    mutation {
                        vacancyRequest (input: {
                            vacancy: "%s"
                            name: "Name"
                            phone: "wrong phone"
                            position: "dev"
                            city: "Москва"
                        }) {
                            ok
                            request {
                                id
                            }
                              errors {
                                field
                                messages
                            }
                        }
                    }
                    """
            % vacancy_id
        )

        with self.assertNumQueries(2):
            res = self.client.post(
                path=self.GRAPHQL_URL,
                data={"query": query, "resume": NamedTemporaryFile(suffix=".doc")},
            )
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["vacancyRequest"]["ok"], False)
        self.assertEqual(content["data"]["vacancyRequest"]["request"], None)
        self.assertEqual(len(content["data"]["vacancyRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["vacancyRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_without_resume(self, mock):
        city = CityFactory()
        manager = ManagerFactory()
        vacancy_category = VacancyCategoryFactory()
        vacancy = VacancyFactory(category=vacancy_category, city=city)
        vacancy_id = to_global_id(VacancyCategoryType.__name__, vacancy.id)

        query = """
                mutation {
                    vacancyRequest (input: {
                        vacancy: "%s"
                        name: "Name"
                        phone: "+79111111111"
                        position: "dev"
                        city: "Москва"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """
        with self.assertNumQueries(4):
            res = self.query(query % vacancy_id)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["vacancyRequest"]["ok"], True)
        request = VacancyRequest.objects.first()
        self.assertEqual(int(content["data"]["vacancyRequest"]["request"]["id"]), request.id)

        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()
        city = CityFactory()
        vacancy_category = VacancyCategoryFactory()
        vacancy = VacancyFactory(category=vacancy_category, city=city)
        vacancy_id = to_global_id(VacancyCategoryType.__name__, vacancy.id)

        query = (
            """
            mutation {
                vacancyRequest (input: {
                    vacancy: "%s"
                    name: "Name"
                    phone: "+79999999999"
                    position: "dev"
                    city: "Москва"
                    graduatedAt: "%s"
                    specialty: "povar"
                    institution: "kitchen"
                }) {
                    ok
                    request {
                        id
                    }
                      errors {
                        field
                        messages
                    }
                }
            }
            """
            % (vacancy_id, now().date()),
        )

        with self.assertNumQueries(4):
            res = self.client.post(
                path=self.GRAPHQL_URL,
                data={"query": query, "resume": NamedTemporaryFile(suffix=".doc")},
            )
        content = json.loads(res.content)
        request = VacancyRequest.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["vacancyRequest"]["ok"], True)
        self.assertEqual(VacancyRequest.objects.all().count(), 1)
        self.assertEqual(int(content["data"]["vacancyRequest"]["request"]["id"]), request.id)
        self.assertNotEqual(request.resume, None)
        self.assertIsNone(content["data"]["vacancyRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class CallbackRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    callbackRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                        interval: "any"
                        timezoneUser: "test/test"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["callbackRequest"]["ok"], False)
        self.assertEqual(content["data"]["callbackRequest"]["request"], None)
        self.assertEqual(len(content["data"]["callbackRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["callbackRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
                mutation {
                    callbackRequest(input: {
                        name: "name"
                        phone: "+79999999999"
                        interval: "any"
                        timezoneUser: "test/test"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["callbackRequest"]["ok"], True)
        self.assertEqual(CallbackRequest.objects.all().count(), 1)
        request = CallbackRequest.objects.all().first()
        self.assertEqual(int(content["data"]["callbackRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["callbackRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class ReservationRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    reservationRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["reservationRequest"]["ok"], False)
        self.assertEqual(content["data"]["reservationRequest"]["request"], None)
        self.assertEqual(len(content["data"]["reservationRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["reservationRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        with self.assertNumQueries(2):
            res = self.query(
                """
                mutation {
                    reservationRequest(input: {
                        name: "name"
                        phone: "+79999999999"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """
            )

        self.assertResponseNoErrors(res)
        content = json.loads(res.content)
        self.assertEqual(content["data"]["reservationRequest"]["ok"], True)
        self.assertEqual(ReservationRequest.objects.all().count(), 1)
        request = ReservationRequest.objects.all().first()
        self.assertEqual(int(content["data"]["reservationRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["reservationRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class ExcursionRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    excursionRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """
        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["excursionRequest"]["ok"], False)
        self.assertEqual(content["data"]["excursionRequest"]["request"], None)
        self.assertEqual(len(content["data"]["excursionRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["excursionRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
                mutation {
                    excursionRequest(input: {
                        name: "name"
                        phone: "+79999999999"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        request = ExcursionRequest.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["excursionRequest"]["ok"], True)
        self.assertEqual(ExcursionRequest.objects.all().count(), 1)
        self.assertEqual(int(content["data"]["excursionRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["excursionRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class DirectorCommunicateRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    directorCommunicateRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                        text: "text"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["directorCommunicateRequest"]["ok"], False)
        self.assertEqual(content["data"]["directorCommunicateRequest"]["request"], None)
        self.assertEqual(len(content["data"]["directorCommunicateRequest"]["errors"]), 1)
        self.assertEqual(
            content["data"]["directorCommunicateRequest"]["errors"][0]["field"], "phone"
        )
        mock.assert_not_called()

    def test_with_wrong_email(self, mock):
        query = """
                mutation {
                    directorCommunicateRequest(input: {
                        name: "name"
                        phone: "+79111111111"
                        email: "wrong email"
                        text: "text"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["directorCommunicateRequest"]["ok"], False)
        self.assertEqual(content["data"]["directorCommunicateRequest"]["request"], None)
        self.assertEqual(len(content["data"]["directorCommunicateRequest"]["errors"]), 1)
        self.assertEqual(
            content["data"]["directorCommunicateRequest"]["errors"][0]["field"], "email"
        )
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
                mutation {
                    directorCommunicateRequest(input: {
                        name: "name"
                        phone: "+79999999999"
                        text: "text"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """
        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        request = DirectorCommunicateRequest.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["directorCommunicateRequest"]["ok"], True)
        self.assertEqual(DirectorCommunicateRequest.objects.all().count(), 1)
        self.assertEqual(
            int(content["data"]["directorCommunicateRequest"]["request"]["id"]), request.id
        )
        self.assertIsNone(content["data"]["directorCommunicateRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


class NewsletterSubscriptionTest(BaseTestCase):
    def test_with_wrong_data(self):
        query = """
                mutation {
                    newsletterSubscription(input: {
                        email: "wrong email"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["newsletterSubscription"]["ok"], False)
        self.assertEqual(content["data"]["newsletterSubscription"]["request"], None)
        self.assertEqual(len(content["data"]["newsletterSubscription"]["errors"]), 1)
        self.assertEqual(content["data"]["newsletterSubscription"]["errors"][0]["field"], "email")

    def test_with_correct_data(self):
        query = """
                mutation {
                    newsletterSubscription(input: {
                        email: "test_email@mail.ru"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(4):
            res = self.query(query)
        content = json.loads(res.content)
        request = NewsletterSubscription.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["newsletterSubscription"]["ok"], True)
        self.assertEqual(NewsletterSubscription.objects.all().count(), 1)
        self.assertEqual(
            int(content["data"]["newsletterSubscription"]["request"]["id"]), request.id
        )
        self.assertIsNone(content["data"]["newsletterSubscription"]["errors"])

    def test_double_subscription(self):
        query = """
                mutation {
                    newsletterSubscription(input: {
                        email: "test_email@mail.ru"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(4):
            self.query(query)

        query = """
                mutation {
                    newsletterSubscription(input: {
                        email: "test_email@mail.ru"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(1):
            res = self.query(query)
        content = json.loads(res.content)
        request = NewsletterSubscription.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["newsletterSubscription"]["ok"], True)
        self.assertEqual(NewsletterSubscription.objects.all().count(), 1)
        self.assertEqual(
            int(content["data"]["newsletterSubscription"]["request"]["id"]), request.id
        )


@patch("request_forms.services.send_mail", new_callable=Mock)
class PurchaseHelpRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    purchaseHelpRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                        propertyType: "%s"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query % PropertyType.FLAT)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["purchaseHelpRequest"]["ok"], False)
        self.assertEqual(content["data"]["purchaseHelpRequest"]["request"], None)
        self.assertEqual(len(content["data"]["purchaseHelpRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["purchaseHelpRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
                mutation {
                    purchaseHelpRequest(input: {
                        name: "name"
                        phone: "+79999999999"
                        propertyType: "%s"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(2):
            res = self.query(query % PropertyType.FLAT)
        content = json.loads(res.content)
        request = PurchaseHelpRequest.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["purchaseHelpRequest"]["ok"], True)
        self.assertEqual(PurchaseHelpRequest.objects.all().count(), 1)
        self.assertEqual(int(content["data"]["purchaseHelpRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["purchaseHelpRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


class TestValidatePhone(BaseTestCase):
    def test_wrong_data(self):
        query = """
                mutation {
                    validatePhone (phone: "wrong phone") {
                        ok
                        phone
                    }
                }
                """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["validatePhone"]["ok"], False)
        self.assertIsNone(content["data"]["validatePhone"]["phone"])

    def test_correct_data(self):
        query = """
                mutation {
                    validatePhone (phone: "+79111111111") {
                        ok
                        phone
                    }
                }
                """
        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["validatePhone"]["ok"], True)
        self.assertEqual(content["data"]["validatePhone"]["phone"], "+79111111111")


@patch("request_forms.services.send_mail", new_callable=Mock)
class CustomRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        form = CustomFormFactory()

        query = """
                mutation {
                    customRequest(input: {
                        form: %d
                        name: "name"
                        phone: "wrong phone"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(1):
            res = self.query(query % form.id)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["customRequest"]["ok"], False)
        self.assertEqual(content["data"]["customRequest"]["request"], None)
        self.assertEqual(len(content["data"]["customRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["customRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_wrong_form(self, mock):
        query = """
                mutation {
                    customRequest(input: {
                        form: 999
                        name: "name"
                        phone: "+79111111111"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """
        with self.assertNumQueries(1):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["customRequest"]["ok"], False)
        self.assertEqual(content["data"]["customRequest"]["request"], None)
        self.assertEqual(len(content["data"]["customRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["customRequest"]["errors"][0]["field"], "form")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()
        form = CustomFormFactory()
        project = ProjectFactory()
        property = FlatFactory(project=project)

        query = """
                mutation {
                    customRequest(input: {
                        form: %d
                        propertyId: "%s"
                        name: "name"
                        phone: "+79999999999"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(6):
            res = self.query(query % (form.id, to_global_id(FlatType.__name__, property.id)))
        content = json.loads(res.content)
        request = CustomRequest.objects.all().first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["customRequest"]["ok"], True)
        self.assertEqual(CustomRequest.objects.all().count(), 1)
        self.assertEqual(int(content["data"]["customRequest"]["request"]["id"]), request.id)
        self.assertEqual(property.id, request.property_id)
        self.assertIsNone(content["data"]["customRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], str(request.form))
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


class ReservationLKRequestMutationTest(BaseTestCase):
    def test_with_correct_data(self):
        project = ProjectFactory()
        property = FlatFactory(project=project)
        query = """
                mutation {
                    reservationLkRequest(input: {
                    property: "%s",
                    projectSlug: "%s",
                    propertyType: "%s"
                }){
                        ok
                        request {
                            id
                        }
                        lkData {
                            name
                            image
                            imagePlan
                            project
                            city
                            house
                            usersRegion
                            price
                            number
                            profitbaseId
                            floor
                            amoPipelineId
                            amoResponsibleUserId
                            bookingPrice
                            bookingPeriod
                            address
                            token
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }      
                """

        property_id = to_global_id("GlobalFlatType", property.id)
        property_type = property.type
        project_slug = project.slug

        response = self.query(query % (property_id, project_slug, property_type))
        self.assertResponseNoErrors(response)


@patch("request_forms.services.send_mail", new_callable=Mock)
class CommercialRentRequestTestCase(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    commercialRentRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["commercialRentRequest"]["ok"], False)
        self.assertEqual(content["data"]["commercialRentRequest"]["request"], None)
        self.assertEqual(len(content["data"]["commercialRentRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["commercialRentRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
                    mutation {
                        commercialRentRequest(input: {
                            name: "name"
                            phone: "+79999999999"
                        }) {
                            ok
                            request {
                                id
                            }
                            errors {
                                field
                                messages
                            }
                        }
                    }
                    """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        request = CommercialRentRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["commercialRentRequest"]["ok"], True)
        self.assertEqual(CommercialRentRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["commercialRentRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["commercialRentRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


class CustomFormEmployeeTestCase(BaseTestCase):
    def test_all_custom_form_employee(self):
        p = ProjectFactory()
        CustomFormEmployeeFactory(project=p)
        [CustomFormEmployeeFactory() for _ in range(2)]

        query = """
        query {
            allCustomFormEmployee(projectSlug: "%s") {
                fullName
                jobTitle
                imageDisplay
                imagePreview
                imagePhoneDisplay
                imagePhonePreview
                form {
                    id
                    yandexMetrics
                    name
                    title
                    description
                }
            }
        }
        """

        with self.assertNumQueries(1):
            resp = self.query(query % p.slug)
        self.assertResponseNoErrors(resp)
        resp_data = resp.json()["data"]["allCustomFormEmployee"]
        self.assertEqual(1, len(resp_data))


@patch("request_forms.services.send_mail", new_callable=Mock)
class MediaRequestTestCase(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
            mutation {
                mediaRequest(input: {
                    name: "name"
                    email: "e@mail.ru"
                    phone: "wrong phone"
                    comment: "some text"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["mediaRequest"]["ok"], False)
        self.assertEqual(content["data"]["mediaRequest"]["request"], None)
        self.assertEqual(len(content["data"]["mediaRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["mediaRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
                    mutation {
                        mediaRequest(input: {
                            name: "name"
                            phone: "+79999999999"
                            email: "e@mail.ru"
                            comment: "hello epta"
                        }) {
                            ok
                            request {
                                id
                            }
                            errors {
                                field
                                messages
                            }
                        }
                    }
                    """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)
        request = MediaRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["mediaRequest"]["ok"], True)
        self.assertEqual(MediaRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["mediaRequest"]["request"]["id"]), request.id)
        self.assertEqual(int(content["data"]["mediaRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["mediaRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class AgentRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        query = """
            mutation {
                agentRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    cityName: ""
                    agencyName: ""
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["agentRequest"]["ok"], False)
        self.assertEqual(content["data"]["agentRequest"]["request"], None)
        self.assertEqual(len(content["data"]["agentRequest"]["errors"]), 2)
        self.assertEqual(content["data"]["agentRequest"]["errors"][0]["field"], "city_name")
        self.assertEqual(content["data"]["agentRequest"]["errors"][1]["field"], "agency_name")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()

        query = """
            mutation {
                agentRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    cityName: "Москва"
                    agencyName: "agencyName"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)
        request = AgentRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["agentRequest"]["ok"], True)
        self.assertEqual(AgentRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["agentRequest"]["request"]["id"]), request.id)
        self.assertEqual(int(content["data"]["agentRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["agentRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class ContractorRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        query = """
            mutation {
                contractorRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    typeOfJob: "type"
                    aboutCompany: "text"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["contractorRequest"]["ok"], False)
        self.assertEqual(content["data"]["contractorRequest"]["request"], None)
        self.assertEqual(len(content["data"]["contractorRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["contractorRequest"]["errors"][0]["field"], "offer")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        query = """
            mutation {
                contractorRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    typeOfJob: "type"
                    aboutCompany: "text"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        with self.assertNumQueries(2):
            res = self.client.post(
                path=self.GRAPHQL_URL,
                data={"query": query, "offer": NamedTemporaryFile(suffix=".doc")},
            )
        content = json.loads(res.content)
        request = ContractorRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["contractorRequest"]["ok"], True)
        self.assertEqual(ContractorRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["contractorRequest"]["request"]["id"]), request.id)
        self.assertEqual(int(content["data"]["contractorRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["contractorRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


class LandingRequestTest(BaseTestCase):
    @patch("request_forms.models.send_mail", new_callable=Mock)
    def test_wrong(self, mock):
        LandingBlockFactory(block_type=LandingBlockChoices.SIMPLE_CTA)

        query = """
                mutation {
                    landingRequest(input: {
                        block: %d
                        email: "eml.ru"
                        name: "pes"
                        phone: "+799999999@@@"
                    }) {
                        ok
                        errors {
                            field
                            messages
                        }
                    }
                }
        """

        resp = self.query(query % 666)
        self.assertResponseNoErrors(resp)

        resp_data = resp.json()
        self.assertEqual(resp_data["data"]["landingRequest"]["ok"], False)
        self.assertEqual(len(resp_data["data"]["landingRequest"]["errors"]), 3)
        self.assertEqual(resp_data["data"]["landingRequest"]["errors"][0]["field"], "phone")
        self.assertEqual(resp_data["data"]["landingRequest"]["errors"][1]["field"], "email")
        self.assertEqual(resp_data["data"]["landingRequest"]["errors"][2]["field"], "block")

        mock.assert_not_called()

    @patch("request_forms.models.send_mail", new_callable=Mock)
    def test_correct(self, mock):
        block = LandingBlockFactory(block_type=LandingBlockChoices.SIMPLE_CTA)

        query = """
                mutation {
                    landingRequest(input: {
                        block: %d
                        email: "e@mail.ru"
                        name: "pes"
                        phone: "+79999999999"
                    }) {
                        ok
                        errors {
                            field
                            messages
                        }
                    }
                }
        """

        resp = self.query(query % block.id)
        self.assertResponseNoErrors(resp)

        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["recipient_list"], ["e@mail.ru"])


@patch("request_forms.services.send_mail", new_callable=Mock)
class AntiCorruptionRequestTest(BaseTestCase):
    def test_incorrect_data(self, mock):
        query = """
            mutation {
                antiCorruptionRequest(input: {
                    name: "name"
                    email: "not email at all"
                    message: "type"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["antiCorruptionRequest"]["ok"], False)
        self.assertEqual(content["data"]["antiCorruptionRequest"]["request"], None)
        self.assertEqual(len(content["data"]["antiCorruptionRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["antiCorruptionRequest"]["errors"][0]["field"], "email")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        query = """
            mutation {
                antiCorruptionRequest(input: {
                    name: "name"
                    email: "e@mail.ru"
                    message: "type"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        res = self.query(query)
        content = json.loads(res.content)
        request = AntiCorruptionRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["antiCorruptionRequest"]["ok"], True)
        self.assertEqual(AntiCorruptionRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["antiCorruptionRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["antiCorruptionRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class TeaserRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        query = """
            mutation {
                teaserRequest(input: {
                    name: "name"
                    phone: "1488"
                    relatedObject: "1488"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["teaserRequest"]["ok"], False)
        self.assertEqual(content["data"]["teaserRequest"]["request"], None)
        self.assertEqual(len(content["data"]["teaserRequest"]["errors"]), 2)
        self.assertEqual(content["data"]["teaserRequest"]["errors"][0]["field"], "phone")
        self.assertEqual(content["data"]["teaserRequest"]["errors"][1]["field"], "related_object")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        slide = MainPageSlideFactory(page=MainPageFactory())
        query = """
            mutation {
                teaserRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    relatedObject: "%s"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        res = self.query(query % slide.id)
        content = json.loads(res.content)
        request = TeaserRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["teaserRequest"]["ok"], True)
        self.assertEqual(TeaserRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["teaserRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["teaserRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class NewsRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        query = """
            mutation {
                newsRequest(input: {
                    name: "name"
                    phone: "1488"
                    relatedObject: "QnVpbGRpbmdUeXBlOjE1NDI0"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["newsRequest"]["ok"], False)
        self.assertEqual(content["data"]["newsRequest"]["request"], None)
        self.assertEqual(len(content["data"]["newsRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["newsRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        news = NewsFactory()
        query = """
            mutation {
                newsRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    relatedObject: "%s"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        res = self.query(query % to_global_id(NewsType.__name__, news.id))
        content = json.loads(res.content)
        request = NewsRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["newsRequest"]["ok"], True)
        self.assertEqual(NewsRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["newsRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["newsRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class OfficeRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        office = OfficeFactory()
        query = """
            mutation {
                officeRequest(input: {
                    name: "name"
                    phone: "1488"
                    relatedObject: "%s"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query % to_global_id(OfficeType.__name__, office.id))
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["officeRequest"]["ok"], False)
        self.assertEqual(content["data"]["officeRequest"]["request"], None)
        self.assertEqual(len(content["data"]["officeRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["officeRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        office = OfficeFactory()
        query = """
            mutation {
                officeRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    relatedObject: "%s"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        res = self.query(query % to_global_id(OfficeType.__name__, office.id))
        content = json.loads(res.content)
        request = OfficeRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["officeRequest"]["ok"], True)
        self.assertEqual(OfficeRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["officeRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["officeRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class LotCardRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        obj = FlatFactory()
        query = """
            mutation {
                lotCardRequest(input: {
                    phone: "1488"
                    relatedObject: "%s"
                    interval: "11 00-12 00"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query % to_global_id(FlatType.__name__, obj.id))
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["lotCardRequest"]["ok"], False)
        self.assertEqual(content["data"]["lotCardRequest"]["request"], None)
        self.assertEqual(len(content["data"]["lotCardRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["lotCardRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        obj = FlatFactory()
        query = """
            mutation {
                lotCardRequest(input: {
                    phone: "+79999999999"
                    relatedObject: "%s"
                    interval: "11 00-12 00"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        res = self.query(query % to_global_id(FlatFactory.__name__, obj.id))
        content = json.loads(res.content)
        request = LotCardRequest.objects.first()
        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["lotCardRequest"]["ok"], True)
        self.assertEqual(LotCardRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["lotCardRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["lotCardRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class FlatListingRequestTest(BaseTestCase):
    def test_all_flat_listing_request_forms(self, mock):
        forms = [FlatListingRequestForm.objects.create(name=f"form {i}") for i in range(5)]

        query = """
        {
        allFlatListingRequestForms {
          name
          description
          buttonName
          }
        }
        """
        resp = self.query(query)
        resp_data = resp.json()["data"]["allFlatListingRequestForms"]

        self.assertResponseNoErrors(resp)
        self.assertEqual(len(forms), len(resp_data))

    def test_incorrect_data(self, mock):
        query = """
            mutation {
                flatListingRequest(input: {
                    name: "name"
                    phone: "1488"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["flatListingRequest"]["ok"], False)
        self.assertEqual(content["data"]["flatListingRequest"]["request"], None)
        self.assertEqual(len(content["data"]["flatListingRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["flatListingRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        query = """
            mutation {
                flatListingRequest(input: {
                    name: "bob"
                    phone: "+79999999999"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """
        res = self.query(query)
        content = json.loads(res.content)
        request = FlatListingRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["flatListingRequest"]["ok"], True)
        self.assertEqual(FlatListingRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["flatListingRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["flatListingRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class StartSaleRequestTestCase(BaseTestCase):
    def test_incorrect_data(self, mock):
        query = """
            mutation {
                startSaleRequest(input: {
                    name: "name"
                    email: "not mail at all"
                    phone: "not correct"
                    projectSlug: "empty"
                    propertyType: "empty"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["startSaleRequest"]["ok"], False)
        self.assertEqual(content["data"]["startSaleRequest"]["request"], None)
        self.assertEqual(len(content["data"]["startSaleRequest"]["errors"]), 4)
        self.assertEqual(content["data"]["startSaleRequest"]["errors"][0]["field"], "email")
        self.assertEqual(content["data"]["startSaleRequest"]["errors"][1]["field"], "phone")
        self.assertEqual(content["data"]["startSaleRequest"]["errors"][2]["field"], "project_slug")
        self.assertEqual(content["data"]["startSaleRequest"]["errors"][3]["field"], "property_type")
        mock.assert_not_called()

    def test_correct_data(self, mock):
        manager = ManagerFactory()
        project = ProjectFactory()

        query = """
            mutation {
                startSaleRequest(input: {
                    name: "name"
                    email: "e@mail.ru"
                    phone: "+79275341597"
                    projectSlug: "%s"
                    propertyType: "%s"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
        """
        res = self.query(query % (project.slug, PropertyType.COMMERCIAL))
        content = json.loads(res.content)
        request = StartSaleRequest.objects.first()

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["startSaleRequest"]["ok"], True)
        self.assertEqual(StartSaleRequest.objects.count(), 1)
        self.assertEqual(int(content["data"]["startSaleRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["startSaleRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request.email_subject)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class CommercialKotelnikiRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    commercialKotelnikiRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                        fromUrl: "https://google.com"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["commercialKotelnikiRequest"]["ok"], False)
        self.assertEqual(content["data"]["commercialKotelnikiRequest"]["request"], None)
        self.assertEqual(len(content["data"]["commercialKotelnikiRequest"]["errors"]), 1)
        self.assertEqual(
            content["data"]["commercialKotelnikiRequest"]["errors"][0]["field"], "phone"
        )
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()
        query = """
            mutation {
                commercialKotelnikiRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                    fromUrl: "https://google.com"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["commercialKotelnikiRequest"]["ok"], True)
        self.assertEqual(CommercialKotelnikiRequest.objects.all().count(), 1)
        request = CommercialKotelnikiRequest.objects.all().first()
        self.assertEqual(
            int(content["data"]["commercialKotelnikiRequest"]["request"]["id"]), request.id
        )
        self.assertIsNone(content["data"]["commercialKotelnikiRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])


@patch("request_forms.services.send_mail", new_callable=Mock)
class ShowRequestTest(BaseTestCase):
    def test_with_wrong_phone(self, mock):
        query = """
                mutation {
                    showRequest(input: {
                        name: "name"
                        phone: "wrong phone"
                    }) {
                        ok
                        request {
                            id
                        }
                        errors {
                            field
                            messages
                        }
                    }
                }
                """

        with self.assertNumQueries(0):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["showRequest"]["ok"], False)
        self.assertEqual(content["data"]["showRequest"]["request"], None)
        self.assertEqual(len(content["data"]["showRequest"]["errors"]), 1)
        self.assertEqual(content["data"]["showRequest"]["errors"][0]["field"], "phone")
        mock.assert_not_called()

    def test_with_correct_data(self, mock):
        manager = ManagerFactory()
        query = """
            mutation {
                showRequest(input: {
                    name: "name"
                    phone: "+79999999999"
                }) {
                    ok
                    request {
                        id
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
            """

        with self.assertNumQueries(2):
            res = self.query(query)
        content = json.loads(res.content)

        self.assertResponseNoErrors(res)
        self.assertEqual(content["data"]["showRequest"]["ok"], True)
        self.assertEqual(ShowRequest.objects.all().count(), 1)
        request = ShowRequest.objects.all().first()
        self.assertEqual(int(content["data"]["showRequest"]["request"]["id"]), request.id)
        self.assertIsNone(content["data"]["showRequest"]["errors"])
        mock.assert_called_once()
        mock_kwargs = mock.call_args.kwargs
        self.assertEqual(mock_kwargs["subject"], request._meta.verbose_name)
        self.assertEqual(mock_kwargs["recipient_list"], [manager.email])
