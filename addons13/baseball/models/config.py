# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class BaseballConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    xml_frbbs_calendar = fields.Char(string='Federation calendar (XML format,)',
        config_parameter='xml_frbbs_calendar',
        help="""URL to an XML file from the federation with access to games information""")