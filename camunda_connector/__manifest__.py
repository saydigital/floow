# -*- coding: utf-8 -*-
{
    'name': "camunda_connector",

    'summary': """
        Add the functionality of camunda to odoo""",

    'author': "Alfadil.tabar@gmail.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/resources.xml',
        'views/porcess_views.xml',
        'views/menus.xml'
    ],


    'qweb': ["static/src/xml/templates.xml"],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
