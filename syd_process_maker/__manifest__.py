# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "BPM - ProcessMaker Integration",
    'summary': """
        SayDigital BPM - ProcessMaker""",

    'description': """
         With this module you can manage :
         
         - Process through ProcessMaker
         
        
         
    """,

    'author': "SayDigital",
    'website': "http://www.saydigital.it",


    'category': 'project',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['syd_bpm'],

    # always loaded
    'data': [
        
        'views/views.xml',
        
    ],
    'installable': True,
    'application': False,
}