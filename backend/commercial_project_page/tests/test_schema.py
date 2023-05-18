from psycopg2.extras import NumericRange

from common.test_cases import BaseTestCase
from mortgage.constants import MortgageType
from mortgage.tests.factories import OfferFactory
from projects.tests.factories import ProjectFactory
from properties.tests.factories import CommercialPremiseFactory

from .factories import (
    CommercialProjectComparisonItemFactory,
    CommercialProjectGallerySlideFactory,
    CommercialProjectComparisonFactory,
    CommercialProjectPageFactory,
    CommercialInvestCardFactory,
    ProjectAudienceFactory,
    AudienceIncomeFactory,
    AudienceFactFactory,
    AudienceAgeFactory,
)


class CommercialProjectPageTest(BaseTestCase):
    def test_default(self):
        projects = [ProjectFactory() for _ in range(3)]
        pages = [CommercialProjectPageFactory(project=projects[i]) for i in range(3)]
        commercial_project_page = pages[0]
        audience = ProjectAudienceFactory(commercial_project_page=commercial_project_page)
        slides = [
            CommercialProjectGallerySlideFactory(commercial_project_page=commercial_project_page)
            for _ in range(5)
        ]
        audience_income = [AudienceIncomeFactory(audience=audience) for _ in range(5)]
        audience_facts = [AudienceFactFactory(audience=audience) for _ in range(4)]
        audience_ages = [AudienceAgeFactory(audience=audience) for _ in range(3)]
        invest_cards = [
            CommercialInvestCardFactory(commercial_project_page=commercial_project_page)
            for _ in range(3)
        ]
        commercial_properties = [
            CommercialPremiseFactory(price=5_000_000 + i, project=projects[i % 3])
            for i in range(10)
        ]
        offers = [
            OfferFactory(
                deposit=NumericRange(20 + i),
                rate=NumericRange(5 + i),
                type=MortgageType.COMMERCIAL,
                projects=[projects[i]],
            )
            for i in range(3)
        ]
        min_commercial_property_price = min([c.price for c in commercial_properties])
        min_offer_deposit = min([o.deposit.lower for o in offers])
        min_offer_rate = min(o.rate.lower for o in offers)
        min_initial_fee = (min_offer_deposit / 100) * min_commercial_property_price

        query = """
        {
        commercialProjectPage(slug: "%s") {
            id
            name
            slug
            minRate
            minInitialFee
            minCommercialPropertyPrice
            aboutText
            aboutTextColored
            aboutImageDisplay
            aboutImagePreview
            video
            videoDuration
            investTitle
            investSubtitle
            investText
            form {
                title
                text
                imageDisplay
                imagePreview
            }
            gallerySlides {
                title
                subtitle
                video
                videoMobile
                imageDisplay
                imagePreview
            }
            project {
                id
                name
                commercialCount
                globalProjectId
            }
            commercialinvestcardSet {
                title
                subtitle
                imageDisplay
                imagePreview
            }
            projectaudience {
                id
                men
                women
                audienceincomeSet {
                    age
                    income
                 }
                audiencefactSet {
                    title
                    subtitle
                }
                audienceageSet {
                    age
                    percent
                }
            }
          }
        }
        """

        with self.assertNumQueries(7):
            resp = self.query(query % commercial_project_page.slug)

        self.assertResponseNoErrors(resp)
        resp_page = resp.json()["data"]["commercialProjectPage"]

        self.assertEqual(resp_page["id"], str(commercial_project_page.id))
        self.assertEqual(resp_page["slug"], commercial_project_page.slug)
        self.assertEqual(resp_page["project"]["name"], commercial_project_page.project.name)
        self.assertEqual(resp_page["projectaudience"]["id"], str(audience.id))
        self.assertEqual(
            len(resp_page["projectaudience"]["audienceincomeSet"]), len(audience_income)
        )
        self.assertEqual(len(resp_page["projectaudience"]["audiencefactSet"]), len(audience_facts))
        self.assertEqual(len(resp_page["projectaudience"]["audienceageSet"]), len(audience_ages))
        self.assertEqual(len(resp_page["commercialinvestcardSet"]), len(invest_cards))
        self.assertEqual(len(resp_page["gallerySlides"]), len(slides))
        self.assertEqual(resp_page["minRate"], min_offer_rate)
        self.assertEqual(resp_page["minInitialFee"], min_initial_fee)
        self.assertEqual(resp_page["minCommercialPropertyPrice"], min_commercial_property_price)

    def test_all_commercial_project_comparison(self):
        comparisons = [CommercialProjectComparisonFactory() for _ in range(6)]
        for c in comparisons:
            c.items.add(*[CommercialProjectComparisonItemFactory() for _ in range(3)])

        query = """
        {
          allCommercialProjectComparison(slug: "%s") {
            id
            title
            items {
              name
              title
              subtitle
            }
          }
        }
        """

        with self.assertNumQueries(2):
            resp = self.query(query % comparisons[0].commercial_project_page.slug)

        self.assertResponseNoErrors(resp)
        resp_data = resp.json()["data"]["allCommercialProjectComparison"]

        self.assertEqual(1, len(resp_data))
        self.assertEqual(resp_data[0]["id"], str(comparisons[0].id))
        self.assertEqual(len(resp_data[0]["items"]), 3)
