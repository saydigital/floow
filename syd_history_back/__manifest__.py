# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "History Back",

    'summary': """
        History Back action""",

    'description': """
        This module adds the history_back client action 
        to action_registry
    """,

    'author': "SayDigital",
    'website': "http://www.saydigital.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','portal'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],
    
    'auto_install': False,
}
