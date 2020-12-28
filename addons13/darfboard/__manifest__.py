{
    'name': "Btetonboard ICO control",
    'version': '1.0',
    'depends': ['base',
                'sale',
                'sales_team',
                'delivery',
                'barcodes',
                'web',
                'mail',
                'website_payment'],
    'author': "Odoochain",
    'category': 'Application',
    'description': """
    Module for synchronization with ICO ERP with IPFS
    """,
    'data': [
     'views/setting_journals.xml',
     #'views/journal_signature.xml',
     
    ],
}