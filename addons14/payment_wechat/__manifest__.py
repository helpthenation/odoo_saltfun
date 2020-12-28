# -*- coding: utf-8 -*-
{
    'name': "Wechat Payment Acquirer",

    'summary': """Payment Acquirer: Wechat Pay Implementation""",

    'description': """
        This module providing Wechat payment acquirer.
    """,

    'author': "Yangtze Dragon",
    'website': "http://www.odoochain.com",

    'category': 'Accounting/Payment Acquirers',
    'version': '14.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['payment'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'data/payment_acquirer_data.xml',
    ],

    "application": True

}
