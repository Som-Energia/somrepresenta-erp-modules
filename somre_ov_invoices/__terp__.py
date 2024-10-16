# -*- coding: utf-8 -*-
{
    "name": "Representation service business layer: Invoices",
    "description": """
        Module to interact with invoices
    """,
    "version": "0-dev",
    "author": "Som Energia",
    "category": "www",
    "depends":[
        "giscere_facturacio",
        "somre_ov_users",
        "somre_ov_installations",
    ],
    "init_xml": [],
    "demo_xml": [
        "demo/giscere_facturacio_demo.xml",
    ],
    "update_xml":[
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
