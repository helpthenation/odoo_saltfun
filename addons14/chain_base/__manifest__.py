# -*- coding: utf-8 -*-
{
    'name': "Base menu for Odoochain",

    'summary': """
        Odoochain base 
     """,

    'author': "Yangtze Loong",
    'maintainer': "Odoochain",
    'website': "https://odoochain.com",

    'category': 'Technical Settings',
    'version': '14.0.0.0',

    'depends': ['web',
                'stock',
                'purchase',
                'contacts',
                ],

    'data': [
        'views/base_menu.xml',
        'views/view_picking_form.xml',
        'views/res_company_view.xml',
    ],

    'installable': True
}
