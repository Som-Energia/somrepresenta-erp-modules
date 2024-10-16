# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _
from .utils import Many2Many


class ResUsers(osv.osv):
    _inherit = 'res.users'

    def _fnt_is_staff(self, cursor, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, False)

        for res_user_id in ids:
            res[res_user_id] = self._is_user_staff(cursor, uid, res_user_id)

        return res

    def _validate_vat(self, cursor, uid, vat):
        partner_obj = self.pool.get("res.partner")
        if not partner_obj.is_vat(vat) or vat[:2] != 'ES':
            raise osv.except_osv('Error validant el VAT!',
                                 'El VAT no és vàlid')
        return vat.upper()

    def process_wizard_create_staff(self, cursor, uid, user, vat, email):

        def has_staff_category(partner):
            return any(cat.id == cat_staff_id for cat in partner.category_id)

        def add_staff_category_to_partner(partner_id):
            return partner_obj.write(cursor, uid, partner_id, {
                "category_id": [Many2Many.link(cat_staff_id)],
            })

        def create_partner(name, vat):
            return partner_obj.create(cursor, uid, {
                'name': name,
                'vat': self._validate_vat(cursor, uid, vat),
                'lang': 'ca_ES',
                "category_id": [Many2Many.set([cat_staff_id])],
            })

        def create_address(name, email, partner_id):
            address_data = {
                'name': name,
                'email': email,
                'partner_id': partner_id,
                'street': 'Carrer Pic de Peguera, 9',
                'zip': '17002',
                'city': 'Girona',
                'state_id': 20,
            }
            return address_obj.create(cursor, uid, address_data)

        def link_user_address(user_id, address_id):
            self.write(cursor, uid, user_id, {'address_id': address_id})

        def set_partner_email(partner, email):
            address_obj.write(cursor, uid, partner.address[0].id, {
                'email': email,
            })

        name = user.name
        user_id = user.id

        partner_obj = self.pool.get("res.partner")
        address_obj = self.pool.get("res.partner.address")
        imd_obj = self.pool.get("ir.model.data")

        # If previously linked, take the linked vat
        address_already_linked = bool(user.address_id)
        if address_already_linked:
            vat = user.address_id.partner_id.vat

        partner_ids = partner_obj.search(cursor, uid, [('vat', '=', vat)])
        if len(partner_ids) > 1:
            return dict(
                info="El VAT de la persona vinculada a la usuària, "
                     "{vat}, està assignat a més persones".format(
                    vat=vat,
                ),
            )

        cat_staff_id = imd_obj.get_object_reference(
            cursor, uid, "somre_ov_users", "res_partner_category_ovrepresenta_staff"
        )[1]

        # No partner found with such vat, create
        if not partner_ids:
            partner_id = create_partner(name, vat)
            address_id = create_address(name, email, partner_id)
            link_user_address(user_id, address_id)

            return dict(
                info="La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa",
            )

        partner = partner_obj.browse(cursor, uid, partner_ids[0])
        if has_staff_category(partner):
            return dict(
                info=(
                    "La persona ja és gestora de l'Oficina Virtual de Representa. "
                    "Potser el VAT {vat} ja està vinculat amb una altra usuària".format(vat=vat)
                )
            )
        add_staff_category_to_partner(partner.id)
        if not partner.address:
            address_id = create_address(name, email, partner.id)
        else:
            address_id = partner.address[0].id
            if not partner.address[0].email:
                set_partner_email(partner, email)

        # Respect existing address id if exists
        if not address_already_linked:
            link_user_address(user_id, address_id)

        warnings = []

        if email and partner.address and partner.address[0].email and partner.address[0].email != email:
            warnings += [
                "Es farà servir el correu ({email}) en comptes de el "
                "provist ({new_email})"
                .format(
                    email=partner.address[0].email,
                    new_email=email,
                )]

        if address_already_linked and user.address_id.email != partner.address[0].email:
            warnings += [
                "L'adreça vinculada a la usuària, {linked}, "
                "no serà la que es farà servir a la OV sinó "
                "la de l'adreça principal de la persona {primary}"
                .format(
                    linked=user.address_id.email,
                    primary=partner.address[0].email,
                )
            ]

        return dict(
            info='.\n'.join([
                "La usuària ha estat convertida en gestora de l'Oficina "
                "Virtual de Representa"
                ] + warnings)
            )

    def init_wizard_create_staff(self, cursor, uid, res_user_id):
        user = self.browse(cursor, uid, res_user_id)

        def error(message, **kwargs):
            return dict(init_message=message, state="init_error", **kwargs)

        def warning(message, **kwargs):
            return dict(init_message=message, **kwargs)

        if not user.address_id:
            return dict(
                vat=None,
                email=None,
            )

        if not user.address_id.partner_id:
            return error(
                "La usuària té una adreça que no està vinculada a cap persona"
            )

        vat = user.address_id.partner_id.vat
        email = user.address_id.partner_id.address[0].email

        if user.is_staff:
            return error(
                "La usuària ja és gestora de l'Oficina Virtual de Representa",
                vat=vat,
                email=email,
            )

        if not vat:
            return error(
                "La persona vinculada per l'adreça de la usuària no té VAT",
            )

        if not email:
            return error(
                "L'adreça primària de la persona vinculada a la usuària no té email",
            )

        res_partner_obj = self.pool.get('res.partner')
        number_of_partners_with_vat = res_partner_obj.search_count(cursor, uid, [
            ('vat', '=', vat),
        ])

        if number_of_partners_with_vat > 1:
            return error(
                "El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(vat=vat),
            )

        if user.address_id.id != user.address_id.partner_id.address[0].id:
            return warning(
                (
                    "L'adreça vinculada a la usuària, {linked}, "
                    "no serà la que es farà servir a la OV sinó "
                    "la de l'adreça principal de la persona {primary}"
                ).format(
                    linked=user.address_id.email,
                    primary=email,
                ),
                vat=vat,
                email=email,
            )

        return dict(
            vat=vat,
            email=email,
        )

    def _is_user_staff(self, cursor, uid, res_user_id):
        imd_obj = self.pool.get("ir.model.data")
        res_user = self.browse(cursor, uid, res_user_id)
        address_id = res_user.address_id
        if not address_id: return False
        partner = address_id.partner_id
        if not partner: return False

        staff_category_id = imd_obj.get_object_reference(
            cursor, uid, "somre_ov_users", "res_partner_category_ovrepresenta_staff"
        )[1]
        return any(cat.id == staff_category_id for cat in partner.category_id)

    def _fnt_is_staff_search(self, cursor, uid, obj, name, args, context=None):
        if not context:
            context = {}
        res = []
        ids = self.search(cursor, uid, [])

        selection_value = args[0][2]

        for res_user_id in ids:
            is_staff = self._is_user_staff(cursor, uid, res_user_id)
            if is_staff == selection_value:
                res.append(res_user_id)

        return [('id', 'in', res)]

    _columns = {
        'is_staff': fields.function(
            _fnt_is_staff,
            fnct_search=_fnt_is_staff_search,
            type='boolean',
            method=True,
            string=_('Gestora OV Representa'),
            store=False,
            bold=True,
        )
    }


ResUsers()
