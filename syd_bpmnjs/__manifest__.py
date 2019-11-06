{
    'name': 'syd_bpmnjs',
    'version': '11.0.1.0.0',
    'summary': '',
    'category': '',
    'author': '',
    'maintainer': '',
    'website': '',
    'license': '',

    'depends': [
        'web', 'syd_bpm'
    ],

    'data': [
        'views/views.xml',
        'views/process_view.xml',

    ],

    'qweb': [
        'static/src/xml/template.xml', ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
