# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from destral import testing
from destral.transaction import Transaction

from ..utils import Many2Many


def get_models(self):
    self.pool = self.openerp.pool
    self.imd = self.pool.get('ir.model.data')
    self.res_users = self.pool.get('res.users')
    self.res_partner = self.pool.get('res.partner')
    self.res_partner_address = self.pool.get('res.partner.address')
    self.wiz_o = self.pool.get('wizard.create.staff.users')


def setup_transaction(self):
    self.txn = Transaction().start(self.database)

    self.cursor = self.txn.cursor
    self.uid = self.txn.user

    def cleanup():
        self.txn.stop()

    self.addCleanup(cleanup)


def reference(self, module, id):
    return self.imd.get_object_reference(
        self.cursor, self.uid, module, id,
    )[1]


class ResUsersTests(testing.OOTestCase):
    get_models = get_models
    setup_transaction = setup_transaction
    reference = reference

    def setUp(self):
        self.maxDiff = None
        self.get_models()
        self.setup_transaction()
        self.cat_staff_id = self.reference("som_ov_users", "res_partner_category_ovrepresenta_staff")
        # A proper staff (primary address linked to user and partner with category)
        self.staff_user_id = self.reference('som_ov_users', 'res_users_already_staff')
        self.staff_partner_id = self.reference('som_ov_users', 'res_partner_res_users_already_staff')
        # Regular partner unrelated to a user and without staff category
        self.non_staff_user_id = self.reference('som_ov_users', 'res_users_non_staff')
        self.non_staff_partner_id = self.reference('som_ov_users', 'res_partner_not_customer')
        self.non_staff_partner_address_id = self.reference('som_ov_users', 'res_partner_address_not_customer')
        # A user with a linked address of a partner witout staff category
        self.linked_non_staff_user_id = self.reference('som_ov_users', 'res_users_linked_non_staff')
        self.linked_non_staff_partner_id = self.reference('som_ov_users', 'res_partner_linked_non_staff')
        self.linked_non_staff_partner_address_id = self.reference('som_ov_users', 'res_partner_address_linked_non_staff')
        # An address without partner
        self.partnerless_address_id = self.reference('som_ov_users', 'res_partner_address_unlinked')
        # Other parther to obtain an existing vat
        self.other_partner_id = self.reference('som_ov_users', 'res_partner_soci')

    def set_user_address(self, user_id, address_id):
        self.res_users.write(self.cursor, self.uid, user_id, {
            'address_id': address_id,
        })

    def add_partner_address(self, partner_id, address_id):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'address': [Many2Many.link(address_id)],
        })

    def add_partner_category(self, partner_id, category_id):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [Many2Many.link(category_id)],
        })

    def set_partner_vat(self, partner_id, vat):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'vat': vat,
        })

    def set_partner_primary_email(self, partner_id, email):
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        primary_address_id = partner.address[0].id
        self.res_partner_address.write(self.cursor, self.uid, primary_address_id, {
            'email': email,
        })

    def test__is_user_staff__user_is_staff(self):
        user_id = self.staff_user_id

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, user_id)

        self.assertTrue(is_staff)

    def test__is_user_staff__user_is_not_staff(self):
        user_id = self.non_staff_user_id

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, user_id)

        self.assertFalse(is_staff)

    def test__init_create_staff__unlinked(self):
        """User has no address linked"""
        user_id = self.non_staff_user_id

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        self.assertEqual(result, dict(
            vat=None,
            email=None,
        ))

    def test__init_create_staff__linked_to_non_staff_partner__takes_data_from_linked(self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        # Then the wizard uses data from the linked partner
        self.assertEqual(result, dict(
            vat=partner.vat,
            email=partner.address[0].email,
        ))

    def test__init_create_staff__linked_partner_already_staff__returns_error(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        self.assertEqual(result, dict(
            vat=partner.vat,
            email=partner.address[0].email,
            state='init_error',
            init_message="La usuària ja és gestora de l'Oficina Virtual de Representa",
        ))

    def test__init_create_staff__linked_to_a_secondary_address__warn_not_the_address_to_be_used(
            self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        secondary_address_id = self.partnerless_address_id
        # Add the new address to the existing one
        self.add_partner_address(partner_id, secondary_address_id)
        # The linked address is not the first one of the partner
        self.set_user_address(user_id, secondary_address_id)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        self.assertEqual(result, dict(
            vat=partner.vat,
            email=partner.address[0].email,  # not "unlinked@somenergia.coop"
            init_message=(
                "L'adreça vinculada a la usuària, {linked}, "
                "no serà la que es farà servir a la OV sinó "
                "la de l'adreça principal de la persona {primary}"
            ).format(
                linked=user.address_id.email,
                primary=partner.address[0].email,
            ),
        ))

    def test__init_create_staff__linked_to_a_partnerless_address__returns_error(self):
        user_id = self.staff_user_id
        # The user address is an unlinked one
        self.set_user_address(user_id, self.partnerless_address_id)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        self.assertEqual(result, dict(
            state='init_error',
            init_message="La usuària té una adreça que no està vinculada a cap persona",
        ))

    def test__init_create_staff__linked_partner_without_vat__returns_error(self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        # Remove the partner VAT
        self.set_partner_vat(partner_id, False)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        self.assertEqual(result, dict(
            state='init_error',
            init_message="La persona vinculada per l'adreça de la usuària no té VAT",
        ))

    def test__init_create_staff__linked_partner_without_email__returns_error(self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        self.set_partner_primary_email(partner_id, False)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        self.assertEqual(result, dict(
            state='init_error',
            init_message="L'adreça primària de la persona vinculada a la usuària no té email",
        ))

    def test__init_create_staff__linked_dupped_vat__returns_error(self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        other_partner_id = self.other_partner_id
        other_partner = self.res_partner.browse(self.cursor, self.uid, other_partner_id)
        # Set the vat of another existing partner
        self.set_partner_vat(partner_id, other_partner.vat)

        result = self.res_users.init_wizard_create_staff(self.cursor, self.uid, user_id)

        # Then the wizard uses data from the linked partner
        self.assertEqual(result, dict(
            state='init_error',
            init_message="El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(
                vat=other_partner.vat),
        ))

    def test__process_create_staff__unlinked_vat_not_found__creates_everything(self):
        """User has no linked address and no partner found with the provided VAT"""
        user_id = self.non_staff_user_id
        vat_not_in_db = 'ESP4594924E'
        email = "user@server.com"
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat_not_in_db,
            email=email,
        )

        self.assertEqual(
            result['info'], "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa")
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        self.assertTrue(user.address_id, "Should be linked to an address")
        self.assertEqual(user.address_id.id, user.address_id.partner_id.address[0].id)
        self.assertEqual(user.address_id.partner_id.vat, vat_not_in_db)
        self.assertEqual(user.address_id.email, email)
        self.assertEqual(user.address_id.name, user.name)
        self.assertEqual(user.address_id.partner_id.name, user.name)
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])

    def test__process_create_staff__unlinked_dupped_vat__returns_error(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        other_partner_id = self.other_partner_id
        other_partner = self.res_partner.browse(self.cursor, self.uid, other_partner_id)
        dupped_vat = other_partner.vat
        # Set the vat of another existing partner
        self.set_partner_vat(partner_id, dupped_vat)
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=dupped_vat,
            email="user@server.com",
        )

        self.assertEqual(
            result['info'],
            "El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(
                vat=other_partner.vat),
        )

    def test__process_create_staff__unlinked_with_category__returns_error(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        vat = partner.vat
        self.add_partner_category(partner_id, self.cat_staff_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat,
            email=partner.address[0].email,  # Same as existing address
        )

        self.assertEqual(
            result['info'],
            "La persona ja és gestora de l'Oficina Virtual de Representa. "
            "Potser el VAT {vat} ja està vinculat amb una altra usuària".format(vat=vat),
        )

    def test__process_create_staff__unlinked_exists_without_category__adds_category(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        vat = partner.vat
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat,
            email=partner.address[0].email,  # Same as existing address
        )

        # Then operation is successful
        self.assertEqual(
            result['info'],
            "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa"
        )
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        # Main partner address is linked to the user
        self.assertEqual(user.address_id.id, self.non_staff_partner_address_id)
        # And category is added to the partner
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])

    def test__process_create_staff__unlinked_exists_without_address(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        vat = partner.vat
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        # Remove the partner address
        self.res_partner.write(self.cursor, self.uid, partner_id, dict(
            address=[Many2Many.set([])],
        ))

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat,
            email="new@email.com",
        )

        # Then operation is successful
        self.assertEqual(
            result['info'],
            "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa"
        )
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        # Main partner address is linked to the user
        self.assertEqual(user.address_id.id, partner.address[0].id)
        # And category is added to the partner
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])

    def test__process_create_staff__unlinked_exists_without_email(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        vat = partner.vat
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        # Remove the partner email
        self.res_partner_address.write(self.cursor, self.uid, partner.address[0].id, dict(
            email=False,
        ))

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat,
            email="new@email.com",
        )

        # Then operation is successful
        self.assertEqual(
            result['info'],
            "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa"
        )
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        # Main partner address is linked to the user
        self.assertEqual(user.address_id.id, partner.address[0].id)
        # Main partner address email is the provided one
        self.assertEqual(partner.address[0].email, "new@email.com")
        # And category is added to the partner
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])

    def test__process_create_staff__unlinked_exists_with_different_email(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        vat = partner.vat
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        new_email = "new@email.com"
        old_email = partner.address[0].email

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat,
            email=new_email,
        )

        # Then operation is successful
        self.assertEqual(
            result['info'],
            "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa.\n"
            "Es farà servir el correu ({email}) en comptes de el provist ({new_email})".format(
                email=old_email,
                new_email=new_email,
            ),
        )
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        # Main partner address is linked to the user
        self.assertEqual(user.address_id.id, partner.address[0].id)
        # Main partner address email is still the old one
        self.assertEqual(partner.address[0].email, old_email)
        # And category is added to the partner
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])

    def test__process_create_staff__linked_to_non_staff_partner__adds_staff_category(self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        old_email = user.address_id.email
        old_address_id = user.address_id.id

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=False, # `readonly` wizard field returns false
            email=False, # `readonly` wizard field returns false
        )

        # Then the operation is successful
        self.assertEqual(
            result['info'],
            "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa"
        )
        # And the staff category is added
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])
        # And the linked address remains
        self.assertEqual(user.address_id.id, old_address_id)
        # And the email remains
        self.assertEqual(user.address_id.email, old_email)

    def test__process_create_staff__linked_to_a_secondary_address__keeps_user_address_id(self):
        user_id = self.linked_non_staff_user_id
        partner_id = self.linked_non_staff_partner_id
        secondary_address_id = self.partnerless_address_id
        # Add the new address to the existing one
        self.add_partner_address(partner_id, secondary_address_id)
        # The linked address is not the first one of the partner
        self.set_user_address(user_id, secondary_address_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        result = self.res_users.process_wizard_create_staff(
            self.cursor, self.uid,
            user=user,
            vat=False, # `readonly` wizard field returns false
            email=False, # `readonly` wizard field returns false
        )

        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        # Then the linked address is kept
        self.assertEqual(user.address_id.id, secondary_address_id)
        # And the result includes a warning
        self.assertEqual(
            result['info'], (
                "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa"
                ".\n"
                "L'adreça vinculada a la usuària, {linked}, "
                "no serà la que es farà servir a la OV sinó "
                "la de l'adreça principal de la persona {primary}"
            ).format(
                linked=user.address_id.email,
                primary=partner.address[0].email,
            )
        )

