# -*- coding: utf-8 -*-
# Copyright (C) 2019-now  山东天骄 https://www.odoochain.cn

{
    'name': "Chain fbprophet",

    'summary': """
        Chain fbprophet integration""",

    'description': """
        This Bridge module interfaces Odoo with forecasting capabilities based on 
        the facebook developed python package fbprophet.
    """,

    'author': 'Yangtze Loong',
    'website': 'https://www.odoochain.com',

    'category': 'Chain',
    'version': '0.0.1',


    'depends': ['base'],

    'external_dependencies': {
        'python': ['pandas',
                   'plotly',
                   ],
    },


    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
