{
    'name': "ERP IPFS ICO control",
    'version': '1.0',
    'depends': ['base',
                'sale',
                'sales_team',
                'delivery',
                'barcodes',
                'mail',
                'web',
                'website_sale',
                'website',
                'website_payment',],
    'author': "Odoochain",
    'category': 'Application',
    'description': """
    Module for synchronization with ICO ERP with IPFS
    """,
    'data': [
     'views/settings.xml',
     #'views/journal_signature.xml',
     
    ],
}