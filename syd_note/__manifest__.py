# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "SayDigital Notes",
    'summary': """
        SayDigital Note Addons""",
    'description': """
         With this module you can manage :
         - Archive notes
         - Archive notes with automated actions
         
    """,

    'author': "SayDigital",
    'website': "http://www.saydigital.it",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['note'],

    # always loaded
    'data': [
        
        'views/views.xml',
        'data/data.xml',
        

    ],
    'installable': True,
    'application': False,
}