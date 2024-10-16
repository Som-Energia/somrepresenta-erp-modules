# -*- coding: utf-8 -*-
{
    "name": "Representation service business layer: Installations",
    "description": """
        Module to interact with installations
    """,
    "version": "0-dev",
    "author": "Som Energia",
    "category": "www",
    "depends":[
        "giscere_cil",
        "giscere_polissa",
        "poweremail",
        "giscere_facturacio",
        "base_iban",
        "somre_ov_users",
    ],
    "init_xml": [],
    "demo_xml": [
        "demo/giscere_instalacio_demo.xml",
    ],
    "update_xml":[
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True
}
