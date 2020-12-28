from odoo import models, fields, api




class UserInvestment(models.Model):
    
    _inherit = 'res.users'
    
    @api.model
    def create(self,values):
        test_of_project = False
        if 'project' in values.keys():
            if values['project']:
                project_creation_dict = {
                    'name':values['project_name'],
                    'market_size':values['market_size'],
                    'cagr':values['cagr'],
                    'planned_share_market':values['planned_share_market'],
                    'market':values['market'],
                    'technology':values['technology'],
                    'total_investment':values['total_investment'],
                    'finance_description':values['finance_description'],
                    }
                print(project_creation_dict)
                #del values['areas']
                del values['project_name']
                del values['market_size']
                del values['cagr']      
                del values['planned_share_market']
                del values['market']
                del values['technology']
                del values['total_investment']
                del values['finance_description']
                print('test of values user create')
                print(values)
                test_of_project = True
            else:
                pass
        else:
            pass
                
        res = super(UserInvestment,self).create(values)
        if 'investor' in values.keys() and test_of_project is False:
            if values['investor']:
                pass
#                 group_project = self.env['res.groups'].search([('category_id.name','=','Project')])
#                 for item_group in group_project:
#                     try:
#                         item_group.write({'users':[(3,res.id)]}) 
#                     except:
#                         pass
        if 'project' in values.keys():
            if values['project']:
                project_creation_dict.update({'user_id':res.id,
                                              'partner_id':res.partner_id.id,
                                              'privacy_visibility':'portal'})
                project_res = self.env['project.project'].create(project_creation_dict)
        return res 
            
class CustomerInvestment(models.Model):
    
    _inherit = 'res.partner'
    
    investment_list = fields.One2many('customer.investment.list','customer_id',string="Customer's investment")
    ethereum_address = fields.Char(string="Ethereum address")
    use_ethereum_address_for_login = fields.Boolean(string="Use ethereum address for login")
    bitcoin_address = fields.Char(string="Bitcoin address")
    investor = fields.Boolean(string="Is investor")
    project = fields.Boolean(string="Is project")
    area_of_investment = fields.Many2many('area.of.investment',string="Areas of investment")
    stage_investing = fields.Many2many('stage.of.investing',string="Stage of investment")
    
    
    @api.model
    def create(self,values):
        res = super(CustomerInvestment,self).create(values)
        return res
    

class CustomerInvestmentList(models.Model):
    
    _name = 'customer.investment.list'
    
    project_of_invest = fields.Many2one('project.project')
    customer_id = fields.Many2one('res.partner')
    project_customer_token_amount = fields.Float(string="Amount of tokens")
    