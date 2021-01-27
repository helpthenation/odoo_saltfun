# -*- coding: utf-8 -*-
{
    'name': "mb_module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'sale', 'account', 'hr_expense', 'base_accounting_kit'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/mb_module_security.xml',
        'views/views.xml',
        'wizards/mb_bdc_signature.xml',
        'wizards/mb_refused.xml',
        'wizards/mb_validated.xml',
        'wizards/list_orders_view_mb.xml',
        'wizards/mb_devis_recu_view.xml',
        'wizards/mb_pv_validation_view.xml',
        'wizards/mb_bdc_fournisseur_view.xml',
        'views/templates.xml',
        'reports/report_stockpicking_operations_inherit.xml',
        'reports/report_invoice_document_inherit.xml',
        'reports/report_purchaseorder_document_inherit.xml',
        'reports/report_saleorder_document_inherit.xml',
        'views/purchase_views_mb_inherit.xml',
        'views/account_move_form_inherit.xml',
        'views/hr_expense_view_form.xml',
        'views/purchase_requisition_views_inherit.xml',
        'views/product_template_tree_view_inherit.xml',
        'views/mb_list_quotation_view.xml',
        'views/account_payement_view_inherit.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
