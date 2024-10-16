# -*- coding: utf-8 -*-
{
    "name": "Representation service business layer: Users",
    "description": """
        Module for Representa Virtual Office integration
    """,
    "version": "0-dev",
    "author": "Som Energia",
    "category": "www",
    "depends":[
        "base_extended",
        "partner_representante",
        "som_ov_signed_documents",
        "poweremail",
    ],
    "init_xml": [],
    "demo_xml": [
        "demo/res_partner_demo.xml",
        "demo/res_users_demo.xml",
    ],
    "update_xml":[
        "wizard/wizard_create_change_password_view.xml",
        "wizard/wizard_create_staff_users_view.xml",
        "data/email_template_data.xml",
        "data/partner_category_data.xml",
        "res_users_view.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
