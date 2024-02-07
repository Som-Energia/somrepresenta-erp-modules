# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import som_ov_production_data

class SomOvProductionDataTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.production_data = self.pool.get('som.ov.production.data')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    def test__measures__base(self):
        result = self.production_data.measures(
            self.cursor, self.uid,
            username='ESW2796397D',
            first_timestamp_utc='2022-01-01T00:00:00Z',
            last_timestamp_utc='2022-01-01T01:00:00Z',
            context=None
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [False, True],
            'first_timestamp_utc': '2022-01-01T00:00:00Z',
            'last_timestamp_utc': '2022-01-01T01:00:00Z',
            'maturity': ['H2', 'H3'],
            'measure_kwh': [80.0, 22.0],
            'foreseen_kwh': [10.0, 22.0],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)


    def test__measures__gaps_filled_with_none(self):
        result = self.production_data.measures(
            self.cursor, self.uid,
            username='ESW2796397D',
            first_timestamp_utc='2021-12-31T23:00:00Z',
            last_timestamp_utc='2022-01-01T02:00:00Z',
            context=None
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [None, False, True, None],
            'first_timestamp_utc': '2021-12-31T23:00:00Z',
            'last_timestamp_utc': '2022-01-01T02:00:00Z',
            'maturity': [None, 'H2', 'H3', None],
            'measure_kwh': [None, 80.0, 22.0, None],
            'foreseen_kwh': [None, 10.0, 22.0, None],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)

    def test__measures__no_such_user(self):
        result = self.production_data.measures(
            self.cursor, self.uid,
            username='username_not_exists',
            first_timestamp_utc='2021-12-31T23:00:00Z',
            last_timestamp_utc='2022-01-01T02:00:00Z',
            context=None
        )

        self.assertEqual(result, dict(
            code='NoSuchUser',
            error='User does not exist',
            trace=result.get('trace', 'NO TRACE AVAILABLE'),
        ))

