# -*- coding: utf-8 -*-
{
    'name': "Chain Environment Check-up",
    'version': '14.0.0.0',
    'summary': """
        Programmatically validate environment, including internal and external
        dependencies""",
    'description': """
This module offers the basic functionalities to validate environment.
    """,

    'author': "Yangtze Loong",
    'maintainer': "Odoochain",
    'website': "https://odoochain.com",

    'category': 'Technical Settings',
    'sequence': 10,
    'license': 'LGPL-3',
    'depends': ['web','chain_base',],

    'data': [
        'views/data.xml',
        'views/views.xml',
        'views/environment_checks.xml'
    ],

    'qweb': ['static/src/xml/templates.xml'],

    'images': [
        'static/description/images/custom_screenshot.png',
        'static/description/images/dependencies_screenshot.png'
    ],

    'installable': True,
    'auto_install': False,
}
