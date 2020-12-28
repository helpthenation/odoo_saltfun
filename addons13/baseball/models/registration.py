# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, exceptions, tools, _
import urllib.request, urllib.error, urllib.parse
import xmltodict
from odoo.exceptions import ValidationError
from datetime import datetime

class Registration(models.Model):
    _name = 'baseball.registration'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'season_id, id'
    _rec_name = 'member_id'

    def get_default_season(self):
        return self.env['baseball.season'].get_current_season().id


    season_id = fields.Many2one("baseball.season", string="Season", default=get_default_season)
    category_id = fields.Many2one("baseball.categories", string="Category", required=True)
    member_id = fields.Many2one("res.partner", string="Member", required=True)
    image_1920 = fields.Image(related='member_id.image_1920')
    image_128 = fields.Image(related='member_id.image_128')
    is_registered = fields.Boolean(default=False, string="Licensed")
    is_certificate = fields.Boolean(default=False, string="Certificate")
    fee_to_pay = fields.Monetary(string="Fee", compute='get_fee_to_pay', store=True, readonly=False)
    fee_paid = fields.Monetary(string="Paid", track_visibility='always', compute='_compute_fee_paid', store=True)
    to_be_paid = fields.Monetary(string="To pay", compute='get_to_be_paid')
    currency_id = fields.Many2one(related='member_id.currency_id')
    payment_date = fields.Date(string="Payment date")
    certificate_id = fields.Many2one("ir.attachment", string="File certificate", compute='_compute_certificate', inverse="_set_certificate")
    stage_id = fields.Many2one('baseball.registration.stage', default=lambda self: self.env['baseball.registration.stage'].search([('is_default','=',True)], limit=1), string='State', group_expand='_expand_states')
    payment_ids = fields.One2many('account.payment', 'membership_id', string="Payments")
    

    @api.depends('category_id', 'season_id')
    def get_fee_to_pay(self):
        for rec in self:
            rec.fee_to_pay = self.env['baseball.fee'].search([
                ('category_id','=',rec.category_id.id),
                ('season_id', '=', rec.season_id.id),
                ]).fee

    @api.depends('fee_to_pay', 'fee_paid')
    def get_to_be_paid(self):
        for rec in self:
            rec.to_be_paid = rec.fee_to_pay - rec.fee_paid

    @api.depends('payment_ids.amount', 'payment_ids.payment_type')
    def _compute_fee_paid(self):
        for rec in self:
            fee_paid = 0
            for payment in rec.payment_ids:
                if payment.payment_type == 'inbound':
                    fee_paid += payment.amount
                elif payment.payment_type == 'outbound':
                    fee_paid -= payment.amount
            rec.fee_paid = fee_paid

    @api.model
    def _expand_states(self, states, domain, order):
        return states.search([], order=order)

    def _compute_certificate(self):
        for rec in self:
            rec.certificate_id = rec.env['ir.attachment'].search([('res_id','=',rec.id),('res_model', '=', rec._name)], limit=1)

    def _set_certificate(self):
        for rec in self:
            if rec.certificate_id.res_id and rec.env['ir.attachment'].search([('res_id','=',rec.id),('res_model', '=', rec._name)]) and  rec.certificate_id.res_id != rec.id:
                raise ValidationError("Cannot pick an attachment already linked to another registration: %s (%s)" % (rec.member_id.name, rec.season_id.name))
            elif rec.certificate_id:
                rec.certificate_id.res_id = rec.id
                rec.certificate_id.res_model = rec._name
                rec.is_certificate = True

    @api.onchange('season_id')
    def onchange_season(self):
        categories = self.member_id.baseball_category_ids.sorted(lambda r: r.cotisation, reverse=True)
        if categories:
            self.category_id = categories[0]

    def action_download_certificate(self):
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/content/%s?download=1' % (self.certificate_id.id),
            'target': 'self',
        }

    def _get_fee_value(self, vals):
        if 'category_id' in vals and 'fee_to_pay' not in vals:
            vals['fee_to_pay'] =  self.env['baseball.fee'].search([
                ('category_id','=', vals['category_id']),
                ('season_id', '=', vals.get('season_id', self.env['baseball.season'].get_current_season().id)),
                ]).fee

    @api.model
    def create(self, values):
        self._get_fee_value(values)
        result = super(Registration, self).create(values)
        result._post_new_registration()
        return result

    def write(self, vals):
        self._get_fee_value(vals)
        result = super(Registration, self).write(vals)
        if any([x in vals for x in ['season_id', 'category_id','is_certificate','fee_paid']]):
            self._post_updade_registration(vals)
        return result


    def _post_new_registration(self):
        template_id = self.env.ref('baseball.mail_template_registration')
        for rec in self:
            rec.member_id._add_role_followers()
            rec.member_id.with_context(current_registration=rec).message_post_with_template(template_id.id)

    def _post_updade_registration(self, vals):
        template_id = self.env.ref('baseball.mail_template_update_registration')
        for rec in self:
            rec.member_id.with_context(current_registration=rec, current_registration_new_vals=vals).message_post_with_template(template_id.id)

    def add_payment(self):
        self.ensure_one()
        return {
            'name': _('Record Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id':self.env.ref('baseball.view_payment_baseball_form').id,
            'context': self.with_context(
                default_membership_id=self.id,
                default_partner_id=self.member_id.id, 
                default_payment_type='inbound',
                default_currency_id=self.currency_id.id,
                default_amount=self.to_be_paid,
                ).env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class RegistrationStage(models.Model):
    _name = 'baseball.registration.stage'
    _order = 'sequence'

    name = fields.Char(string="Name")
    fold = fields.Boolean(default=False)
    discard_stage = fields.Boolean(default=False)
    is_default = fields.Boolean(default=False)
    sequence = fields.Integer()
    

class Fee(models.Model):
    _name = 'baseball.fee'

    fee = fields.Float(string="Fee")
    season_id = fields.Many2one("baseball.season", string="Season")
    category_id = fields.Many2one("baseball.categories", string="Category")
