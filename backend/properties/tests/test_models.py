from django.test import TestCase
from django.utils.timezone import now, timedelta

from .factories import SpecialOfferFactory
from ..services import update_special_offers_activity


class SpecialOfferTest(TestCase):
    def test_update_activity(self):
        # 1
        offer = SpecialOfferFactory()
        update_special_offers_activity()
        offer.refresh_from_db()
        self.assertTrue(offer.is_active)

        # 2
        offer = SpecialOfferFactory(finish_date=now() - timedelta(days=1))
        update_special_offers_activity()
        offer.refresh_from_db()
        self.assertFalse(offer.is_active)

        # 3
        offer = SpecialOfferFactory(start_date=now() + timedelta(days=1))
        update_special_offers_activity()
        offer.refresh_from_db()
        self.assertFalse(offer.is_active)

        # 4
        offer = SpecialOfferFactory(
            start_date=now() + timedelta(days=1), finish_date=now() + timedelta(days=2)
        )
        update_special_offers_activity()
        offer.refresh_from_db()
        self.assertFalse(offer.is_active)

        # 5
        offer = SpecialOfferFactory(
            start_date=now() - timedelta(days=2), finish_date=now() - timedelta(days=1)
        )
        update_special_offers_activity()
        offer.refresh_from_db()
        self.assertFalse(offer.is_active)
