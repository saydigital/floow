# -*- coding: utf-8 -*-
{
    "name": "camunda_connector",
    "summary": """
        Add the functionality of camunda to odoo""",
    "author": "Alfadil.tabar@gmail.com",
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/resources.xml",
        "views/porcess_views.xml",
        "wizards/start_process_views.xml",
        "views/process_instance_views.xml",
        "views/menus.xml",
        "data/sequence.xml",
    ],
    "qweb": ["static/src/xml/templates.xml"],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
