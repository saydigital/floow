# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "saydigital Note Name",

    'summary': """
        With this module you can give a name to a note """,

    'description': """
        With this module you can give a name to a note
    """,

    'author': "saydigital",
    'website': "http://www.saydigital.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','syd_note'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views_note_name.xml',
    ],
    # only loaded in demonstration mode
    
}