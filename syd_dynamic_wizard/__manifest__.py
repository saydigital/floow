# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "Dynamic Wizard",

    'summary': """
        Dynamic Wizard """,

    'description': """
        Dynamic Wizard 
    """,

    'author': "SayDigital",
    'website': "http://www.saydigital.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/views.xml',
     
        'security/ir.model.access.csv',
    ]
}