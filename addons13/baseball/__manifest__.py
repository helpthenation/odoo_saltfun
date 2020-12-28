# -*- coding: utf-8 -*-
{
    'name': "baseball",
    'summary': """Baseball club management module""",
    'description': """

    """,
    'author': "Stanislas Sobieski",
    'website': "http://www.msgphoenix.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'contacts', 'calendar', 'auth_signup', 'website_blog', 'sale_management', 'website_sale'],

    # always loaded
    'data': [
        'data/groups.xml',
        'data/partners.xml',
        'data/initial_values.xml',
        # 'data/menus.xml',
        'data/teams.xml',
        'data/delete.xml',
        'data/product.xml',
        'data/cron.xml',
        'data/mails.xml',
        'data/sponsors.xml',
        'data/stage.xml',
        'security/ir.model.access.csv',
        'wizard/practice_wizard.xml',
        'wizard/practice_template.xml',
        'views/menus.xml',
        'views/members.xml',
        'views/registration.xml',
        'views/users.xml',
        'views/categories.xml',
        'views/teams.xml',
        'views/divisions.xml',
        'views/role.xml',
        'views/logos.xml',
        'views/products.xml',
        'views/games.xml',
        'views/event.xml',
        'views/tournament.xml',
        'views/positions.xml',
        'views/venue.xml',
        'views/season.xml',
        'views/club.xml',
        'views/account_payment.xml',
        # 'views/config.xml',
        'views/sponsors.xml',
        'views/practices.xml',
        # 'views/pages/layout.xml',
        # 'views/pages/homepage.xml',
        # 'views/pages/signup.xml',
        # 'views/pages/teams.xml',
        # 'views/pages/practices.xml',
        # 'views/pages/baseball.xml',
        # 'views/pages/register.xml',
        # 'views/pages/club.xml',
        # 'views/pages/calendar.xml',
        # 'views/pages/blog.xml',
        # 'views/pages/website_sale.xml',
        # 'views/snippets.xml',
        # 'views/pages/snippets/snippets.xml',
        # 'views/pages/profile.xml',
        # 'views/pages/sponsors.xml',
        # 'views/pages/coach_corner.xml',
    ],
}
