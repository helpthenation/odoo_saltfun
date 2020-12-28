# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import base64
import datetime
from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from ast import literal_eval
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website.controllers.main import Website
import werkzeug
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Website(Website):
    @http.route(auth='public')
    def index(self, data={},**kw):
        super(Website, self).index(**kw)
        projects_list = request.env['project.project'].sudo().search([])
        project_list = []
        project_item_dict = {}
        #if request.env.user.partner_id:
        #    partner = request.env.user.partner_id
        for project_item in projects_list:
            #projects_customer = request.env['customer.investment.list'].search([('customer_id','=',partner.id),
            #'project_token_amount':projects_customer.project_customer_token_amount,                                                                    ('project_of_invest','=',project_item.id)])
            project_item_dict.update({'project_name':project_item.name,
                                      'project_token_name':project_item.project_token_name,
                                      'token_amount':project_item.token_amount,
                                      'id':project_item.id,
                                      'project':project_item,
                                      'publish_on_web':project_item.publish_on_web,
                                        })
            project_list.append(project_item_dict)
            project_item_dict = {}
            data.update({'projects':project_list})
            print(data)
        return http.request.render('darfproject.homepage_projects', data)

class AuthSignupHome(AuthSignupHome):

    def _signup_with_values(self, token, values):
        print(values)
        qcontext = request.params.copy()
        print(qcontext)
        if qcontext.get('investor',False):
            values.update(investor=True)
            values.update(ethereum_address=qcontext.get('investor_address',False))
            list_of_areas = []
            list_of_stage = []
            for item_of_qcontext in qcontext.keys():
                if item_of_qcontext.split('-')[0] == 'treeselect':
                    if qcontext[item_of_qcontext].split('_')[0] == 'area':
                        list_of_areas.append(int(qcontext[item_of_qcontext].split('_')[1]))
                    if qcontext[item_of_qcontext].split('_')[0] == 'stage':
                        list_of_stage.append(int(qcontext[item_of_qcontext].split('_')[1]))
            print("test of areas:",list_of_areas)
            values.update(area_of_investment = [(6,0,list_of_areas)])
            values.update(stage_investing = [(6,0,list_of_stage)])
        if qcontext.get('project',False):
            print('test of get !!!')
            values.update(project=True)
            project_name = qcontext.get('project_name',False)
            #insert in values parameters for project creationg
            values.update(project_name=project_name)
            values.update(market_size=qcontext.get('market_size'))
            values.update(cagr=qcontext.get('cagr'))
            values.update(planned_share_market=qcontext.get('planned_share_market'))
            values.update(market=qcontext.get('market'))
            values.update(technology=qcontext.get('technology'))
            values.update(total_investment=qcontext.get('total_investment'))
            values.update(finance_description=qcontext.get('finance_description'))
        print('test of values:',values)
        return super(AuthSignupHome, self)._signup_with_values(token, values)
    
    
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                            password=request.params.get('password')
                        ).send_mail(user_sudo.id, force_send=True)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")
        print(qcontext)
        get_area_of_investing = request.env['area.of.investment'].sudo().search([])
        get_area_of_investing_category = request.env['area.of.investment.category'].sudo().search([])
        get_stage_investing = request.env['stage.of.investing'].sudo().search([])
        
        qcontext.update({'areas':get_area_of_investing,
                         'categories':get_area_of_investing_category,
                         'stage_invest':get_stage_investing})
        
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
class CustomerPortal(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        projects = request.env['customer.investment.list'].search([('customer_id','=',partner.id)])
        projects_list = request.env['project.project'].sudo().search([])
        print(projects)
        projects_customer_list = []
        if projects:
            for project_item in projects:
                project_item_dic = {}
                project_item_dic.update({'project_name':project_item.project_of_invest.name,
                                        'project_token_name':project_item.project_of_invest.project_token_name,
                                        'token_amount':project_item.project_of_invest.token_amount,
                                        'project_token_amount':project_item.project_customer_token_amount,
                                        'id':project_item.project_of_invest.id,
                                        'publish_on_web':project_item.publish_on_web,
                                        })
                projects_customer_list.append(project_item_dic)
        else:
            project_item_dic = {}
        print(projects_customer_list)
        values.update({
            'projects': projects_customer_list,
        })
        project_list = []
        project_item_dict = {}
        for project_item in projects_list:
            print(project_item)
            
            projects_customer = request.env['customer.investment.list'].search([('customer_id','=',partner.id),
                                                                                ('project_of_invest','=',project_item.id)])
            project_item_dict.update({'project_name':project_item.name,
                                      'project_token_name':project_item.project_token_name,
                                      'token_amount':project_item.token_amount,
                                      'project_token_amount':projects_customer.project_customer_token_amount,
                                      'id':project_item.id,
                                      'project':project_item,
                                      'publish_on_web':project_item.publish_on_web,
                                        })
            project_list.append(project_item_dict)
            project_item_dict = {}
            
        print(project_list)
        values.update({'projects_list':project_list})
        return values
    
    
    @http.route(['/my/home/project/<int:project>'], type='http', auth="public", website=True)
    def project_page(self, project, **kw):
        project = request.env['project.project'].browse([project])
        project_sudo= project.sudo()
        partner = request.env.user.partner_id
        return request.render("darfproject.project_page", {
            'project': project_sudo,
        })

    @http.route(['/my/home/projectsboard'], type='http', auth="user", website=True)
    def project_board(self, **kw):
        project = request.env['project.project'].sudo().search([])
        project_sudo= project.sudo()
        print(project)
        partner = request.env.user.partner_id
        project_list = []
        project_item_dict = {}
        for project_item in project:
            print(project_item)
            
            projects_customer = request.env['customer.investment.list'].search([('customer_id','=',partner.id),
                                                                                ('project_of_invest','=',project_item.id)])
            project_item_dict.update({'project_name':project_item.name,
                                      'project_token_name':project_item.project_token_name,
                                      'token_amount':project_item.token_amount,
                                      'project_token_amount':projects_customer.project_customer_token_amount,
                                      'id':project_item.id,
                                      'project':project_item,
                                      'publish_on_web':project_item.publish_on_web,
                                        })
            project_list.append(project_item_dict)
            project_item_dict = {}
            
        print(project_list)
        return request.render("darfproject.projects_board", {
            'projects': project_list,
        })

    @http.route(['/my/home/invest/<int:project>'], type='http', auth="user", website=True)
    def project_invest(self, project, **kw):
        project = request.env['project.project'].browse([project])
        project_sudo= project.sudo()
        partner = request.env.user.partner_id
        print(project_sudo)
        return request.render("darfproject.project_invest", {
            'project': project_sudo,
        })

    @http.route(['/my/home/setting'], type='http', auth="user", website=True)
    def customer_setting(self,  **kw):
        partner = request.env.user.partner_id
        print(partner)
        return request.render("darfproject.customer_setting", {
            'customer': partner,
        })

    @http.route(['/web/condition'], type='json', auth="user", website=True)
    def buy_condition(self, project_id,token_value, **kw):
        partner = request.env.user.partner_id
        print(project_id, token_value)
        return True

    @http.route(['/web/buytoken'], type='json', auth="user", website=True)
    def buy_tokens(self, project_id,accept,token_value, **kw):
        partner = request.env.user.partner_id
        print(project_id, token_value,'test accept', accept,'partner_id:',partner.id)
        project_id = int(project_id)
        get_list = request.env['customer.investment.list'].search([('customer_id','=',partner.id),('project_of_invest','=',project_id)])
        if get_list:
            print(get_list)
            token_value = get_list.project_customer_token_amount + int(token_value)
            get_list.write({'project_customer_token_amount':token_value})
        else:
            dict_for_write = {'project_of_invest':project_id,
                              'project_customer_token_amount':token_value}
            print(dict_for_write)
            partner.write({'investment_list':[(0,0,dict_for_write)]})
        return True

    @http.route(['/my/home/condition/<int:project_id>/<int:token_value>'], type='http', auth="user", website=True)
    def buy_condition_page(self, project_id,token_value,  **kw):
        partner = request.env.user.partner_id
        project = request.env['project.project'].browse([project_id])
        return request.render("darfproject.term_and_condition", {
            'project': project,
            'token_value':token_value,
                        })
