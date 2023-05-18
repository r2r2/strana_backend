from datetime import date
from django.utils.timezone import now, timedelta
from common.test_cases import BaseTestCase
from common.utils import get_quarter_from_month
from .factories import BuildingFactory
from ..services import calculate_current_level, calculate_building_finish_dates


class TestBuildingWithCurrentLevel(BaseTestCase):
    def test_calculate_current_level(self):
        n = now().date()
        start_date = n - timedelta(days=365)
        finish_date = n + timedelta(days=365)
        b = BuildingFactory(current_level=0, start_date=start_date, fact_date=finish_date)

        calculate_current_level()
        b.refresh_from_db()

        # in the middle of two dates, it means progress is 50%
        self.assertEqual(50, b.current_level)

    def test_calculate_current_level_with_no_dates(self):
        b = BuildingFactory(current_level=77)

        calculate_current_level()
        b.refresh_from_db()

        # same
        self.assertEqual(77, b.current_level)

    def test_calculate_current_level_almost_done(self):
        n = now().date()
        start_date = n - timedelta(days=36555)
        finish_date = n + timedelta(days=365)
        b = BuildingFactory(current_level=0, start_date=start_date, fact_date=finish_date)

        calculate_current_level()
        b.refresh_from_db()

        # almost done
        self.assertEqual(99, b.current_level)

    def test_calculate_current_level_with_same_dates(self):
        n = now().date()
        b = BuildingFactory(current_level=5, start_date=n, fact_date=n)

        calculate_current_level()
        b.refresh_from_db()

        # same
        # из-за того, что fact_date равен start_date возникает DataError: division by zero
        # такие корпуса игнорируются
        self.assertEqual(5, b.current_level)

    def test_calculate_current_level_one_day(self):
        n = now().date()
        b = BuildingFactory(current_level=0, start_date=n, fact_date=n + timedelta(days=1))

        calculate_current_level()
        b.refresh_from_db()

        self.assertEqual(0, b.current_level)

    def test_calculate_current_level_107_percent(self):
        start = date(2020, 7, 1)
        fact = date(2021, 12, 31)
        b = BuildingFactory(current_level=0, start_date=start, fact_date=fact + timedelta(days=1))

        calculate_current_level()
        b.refresh_from_db()

        self.assertEqual(100, b.current_level)


class TestBuildingWithFinishDated(BaseTestCase):
    def test_default(self):
        b = BuildingFactory(built_year=None, ready_quarter=None)
        finish_date = b.finish_date
        self.assertIsNotNone(finish_date)

        calculate_building_finish_dates()

        b.refresh_from_db()
        self.assertEqual(finish_date.year, b.built_year)
        self.assertEqual(get_quarter_from_month(finish_date.month), b.ready_quarter)
