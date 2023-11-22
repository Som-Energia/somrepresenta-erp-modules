# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from destral import testing
from destral.transaction import Transaction

from .. import installation


class SomInstallationsTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.installation = self.pool.get('installation')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    def test__get_installations_by__user_exists_is_active_and_have_installations(self):
        a_partner_vat = 'ES48591264S'

        result = self.installation.get_installations_by(self.cursor, self.uid, a_partner_vat)

        expected_result = [
            dict(
                contract_number='000',
                installation_name='Installation 0',
            ),
            dict(
                contract_number='000',
                installation_name='Installation 1',
            ),
        ]
        self.assertEqual(expected_result, result)

    def test__get_installations_by__user_not_exists(self):
        an_invalid_partner_vat = 123

        result = self.installation.get_installations_by(self.cursor, self.uid, an_invalid_partner_vat)

        self.assertEqual(result['code'], 'PartnerNotExists')

    def test__get_installation_details_by__base(self):
        an_installation_name = 'Installation 0'

        result = self.installation.get_installation_details_by(self.cursor, self.uid, an_installation_name)

        expected_result = dict(
            installation_details=dict(
                contract_number='000',
                name = 'Installation 0',
                address = 'Carrer Buenaventura Durruti 666 aclaridor 08080 (Girona)',
                city = 'Girona',
                postal_code='08080',
                province='Girona',
                coordinates = '41.54670,0.80284',
                ministry_code = 'RE-00000',
                technology = False,
                cil='ES1234000000000001JK1F001',
                rated_power=800.0,
                type = 'IT-00000',
            ),
            contract_details=dict(
                billing_mode=False,
                discharge_date='2022-02-22',
                remuneration_service=False,
                representation_type='indirecta_cnmc',
                status='esborrany',
            ),
        )
        self.assertEqual(expected_result, result)
