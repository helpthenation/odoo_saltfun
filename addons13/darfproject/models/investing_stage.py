from odoo import models, fields, api, SUPERUSER_ID


class StageOfInvesting(models.Model):
    
    _name = 'stage.of.investing'
    
    name = fields.Char(string="Name of stage")