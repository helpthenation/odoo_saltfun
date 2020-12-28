# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID

from odoo import models, fields
from odoo.addons.mail.models.update import PublisherWarrantyContract

def update_notification(self, cr, uid, ids, cron_mode=True, context=None):
    self.pool['ir.config_parameter'].set_param(cr, SUPERUSER_ID, 'database.expiration_date', '9999-01-01', ['base.group_user'])
    self.pool['ir.config_parameter'].set_param(cr, SUPERUSER_ID, 'database.expiration_reason', 'None', ['base.group_system'])
    self.pool['ir.config_parameter'].set_param(cr, SUPERUSER_ID, 'database.enterprise_code', '12345678890', ['base.group_user'])
    return True

PublisherWarrantyContract.update_notification = update_notification
