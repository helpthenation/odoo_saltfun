# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import xmlrpc.client
from odoo import fields, models, api
import base64
import logging

_logger = logging.getLogger(__name__)


class StockPickingConnector(models.Model):
    _inherit = 'stock.picking'

    last_change = fields.Datetime('Última modificación')
    remote_state = fields.Boolean('Enviado')

    # BORRAR Para instalr en Green
    # x_kg_estimado_porte = fields.Integer('Kg')
    # x_loggo_origen = fields.Many2one('res.partner')
    # x_loggo_destino = fields.Many2one('res.partner')
    # x_loggo_pedido = fields.Char('Pedido en Loggo')
    # x_loggo_recoger_date = fields.Datetime('recoger')
    # x_loggo_entregar_date = fields.Datetime('entregar')
    # x_loggo_nota = fields.Text('Nota')


    def setxmlrpc(self):

        if not self.env.user.company_id.remote_db or not self.env.user.company_id.remote_url:
            raise Warning((
                "Revise los campos 'Instancia' y 'Servidor' en la pestaña LOGGO"
            ))
        elif not self.env.user.company_id.remote_user or not self.env.user.company_id.remote_pass:
            raise Warning((
                "You must specify a user and remote access password."
            ))
        else:

            try:
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(
                    self.env.user.company_id.remote_url))
                uid = common.authenticate(
                    self.env.user.company_id.remote_db,
                    self.env.user.company_id.remote_user,
                    self.env.user.company_id.remote_pass, {})
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(
                    self.env.user.company_id.remote_url))
            except Exception as e:
                raise Warning(("Exception when calling remote server $common: %s\n" % e))
            return {
                'uid': uid,
                'models': models,
                'db': self.env.user.company_id.remote_db,
                'rpcu': self.env.user.company_id.remote_user,
                'rpcp': self.env.user.company_id.remote_pass,
            }


    def set_remote_company(self, conn):
        try:
            usuario_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'],
                                                   'res.users', 'search_read',
                                                   [[('login', '=', self.env.user.company_id.remote_user)]],
                                                   {'fields': ['company_id'], 'limit': 1})
        except Exception as e:
            raise Warning(("Exception when calling remote server $Remote User Get company: %s\n" % e))

        if len(usuario_id) > 0:
            if usuario_id[0]['company_id'][0] != self.env.user.company_id.remote_company_id:
                try:
                    loggo_company_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'],
                                                                 'res.users', 'write',
                                                                 [usuario_id[0]['id'],
                                                                  {
                                                                      'company_id': self.env.user.company_id.remote_company_id}])
                except Exception as e:
                    raise Warning(("Exception when calling remote server $Remote User Company_id: %s\n" % e))
        else:
            raise Warning(("No existe el Usuario en GlobalParis PYC SERLOGIT \n"))


    def get_line_description(self, picking):

        description = "Recogida en " + str(picking.x_loggo_origen.name) + " hasta " + str(picking.x_loggo_destino.name) \
                      + " de " + str(picking.x_loggo_kg) + "Kg " + " SEGÚN ALBARÁN GREEN " + picking.name + " " + \
                      "Fecha inicio " + str(picking.x_loggo_recoger_date) + "Fecha fin " + str(
            picking.x_loggo_entregar_date)

        return description


    def compose_order_line(self, conn, origin_id, delivery_id, description, record):

        company_id = self.env.user.company_id

        try:
            check_remote_product_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'],
                                                                'product.product', 'search_read',
                                                                [[('name', '=',
                                                                   self.env.user.company_id.remote_product_name)]],
                                                                {'fields': ['id'], 'limit': 1})
        except Exception as e:
            raise Warning(("Exception when calling remote server $Remote Product Name %s\n" % e))

        if not len(check_remote_product_id) > 0:
            try:
                remote_product_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'],
                                                              'product.product', 'create',
                                                              [{
                                                                  'name': self.env.user.company_id.remote_product_name,
                                                                  'type': 'service',
                                                                  'sale_ok': True,
                                                                  'purchase_ok': False,
                                                              }])
                company_id.porte_green_product_id = remote_product_id
            except Exception as e:
                raise Warning(("Exception when calling remote server $RemoteProductCreate: %s\n" % e))

        remote_product_id = company_id.porte_green_product_id

        if remote_product_id:
            try:
                product_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'],
                                                       'product.product', 'search',
                                                       [[
                                                           ('id', '=', remote_product_id),
                                                       ]],
                                                       {'limit': 1})
            except Exception as e:
                raise Warning(("Exception when calling remote server $RemoteProductId: %s\n" % e))

            order_line = {
                'product_id': product_id[0],
                'name': description,
                # 'origin_id': origin_id,
                # 'delivery_id': delivery_id,
                'product_uom_qty': '1',
                # 'planned_date_begin': record.x_loggo_recoger_date,
                # 'planned_date_end': record.x_loggo_entregar_date,
            }
            return order_line
        else:
            raise Warning(("The destination does not have the necessary products"))


    def create_attachment(self, conn, report, report_type, sale_order_id):

        report_id = report_type
        pdf = self.env.ref(report_id).render_qweb_pdf(report.id)

        # pdf result is a list
        b64_pdf = base64.b64encode(pdf[0])
        name = report.x_name

        attachment_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'], 'ir.attachment', 'create',
                                                  [{
                                                      'name': name + '.pdf',
                                                      'type': 'binary',
                                                      'datas': b64_pdf,
                                                      'display_name': name + '.pdf',
                                                      'store_fname': name,
                                                      'res_model': 'sale.order',
                                                      'res_id': sale_order_id,
                                                      'mimetype': 'application/pdf'
                                                  }])
        return attachment_id


    def create_message_post(self, conn, sale_order_id, attachment_ids):
        try:
            message_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'], 'mail.message',
                                                   'create',
                                                   [{
                                                       'res_id': sale_order_id,
                                                       'model': 'sale.order',
                                                       'body': 'Documentos',
                                                       'attachment_ids': [(6, 0, attachment_ids)],
                                                   }])
            return message_id
        except Exception as e:
            raise Warning(("Exception when calling remote server $Message_post: %s\n" % e))


    def create_sale_order(self, conn, picking, partner_id, description, order_line):
        if not picking.x_loggo_pedido:
            try:
                sale_order_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'], 'sale.order', 'create',
                                                          [{
                                                              'partner_id': partner_id,
                                                              'company_id': self.env.user.company_id.remote_company_id,
                                                              'note': str(description) + str(picking.x_loggo_nota),
                                                              'order_line': [(0, 0, order_line)],
                                                          }])
            except Exception as e:
                raise Warning(("Exception when calling remote server $SO Name: %s\n" % e))
            if sale_order_id:
                try:
                    sale_order_id_name = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'], 'sale.order',
                                                                   'read', [sale_order_id],
                                                                   {'fields': ['name']})
                    return [sale_order_id, sale_order_id_name[0]['name']]
                except Exception as e:
                    raise Warning(("Exception when calling remote server $SO create: %s\n" % e))
        else:
            return False


    def check_partner(self, conn, partner):

        if not partner:
            raise Warning(("Debe seleccionar 'Recoger en' y 'Entregar en' antes de generar el pedido \n"))
        else:
            if partner.remote_id:
                try:
                    remote_partner_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'],
                                                                  'res.partner', 'search',
                                                                  [[
                                                                      ('id', '=', partner.remote_id),
                                                                  ]],
                                                                  {'limit': 1})
                except Exception as e:
                    raise Warning(("Exception when calling remote server $RemotePartnerId: %s\n" % e))
                if remote_partner_id:
                    return remote_partner_id[0]
            else:
                remote_partner_id = self.create_partner(conn, partner)
                partner.remote_id = remote_partner_id
                return remote_partner_id


    def create_partner(self, conn, partner):

        try:
            partner_id = conn['models'].execute_kw(conn['db'], conn['uid'], conn['rpcp'], 'res.partner', 'create', [{
                'name': partner.name,
                'company_type': partner.company_type,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id.id,
                'zip': partner.zip,
                'country_id': partner.country_id.id,
                'vat': partner.vat,
                # 'x_km': ,
                'phone': partner.phone,
                # 'mobile': partner.mobile,
                'email': partner.email,
                'website': partner.website,
                # 'comment': partner.comment,

            }])
            return partner_id
        except Exception as e:
            raise Warning(("Exception when calling remote server $Partner_ID Create: %s\n" % e))


    def create_loggo_sale_order(self):
        for record in self:
            conn = self.setxmlrpc()
            self.set_remote_company(conn)

            # El cliente en GP
            company_id = self.env.user.company_id

            # green_company_id = self.env['res.company'].sudo().search([('vat', '=', 'ESB73862864')], limit=1)
            # if not green_company_id:
            #    raise Warning(("No se encuentra la compañia con VAT ESB73862864" ))
            # Comprueba si los partners existen para poder crear el SO
            partner_id = self.check_partner(conn, company_id.partner_id)
            origin_id = self.check_partner(conn, record.x_loggo_origen)
            delivery_id = self.check_partner(conn, record.x_loggo_destino)

            description = self.get_line_description(record)
            order_line = self.compose_order_line(conn, origin_id, delivery_id, description, record)

            if description:

                print(partner_id, self.env.user.company_id.remote_company_id, description, order_line,
                      record.x_loggo_nota)

                sale_order_data = self.create_sale_order(conn, record, partner_id, description, order_line)

                if sale_order_data:
                    record.x_loggo_pedido = sale_order_data[1]
                    attachment_ids = []
                    report_type_di = 'studio_customization.documento_de_identif_1d084d06-1300-4837-87cb-2fe21db280a4'
                    report_type_nt = 'studio_customization.notificaciones_de_tr_5f9525dc-164d-467e-8819-eceaf852ee1b'
                    for report in record.x_di_ids:
                        if report.x_nt_id:
                            attachment_id = self.create_attachment(conn, report, report_type_di, sale_order_data[0])
                            attachment_ids.append(attachment_id)
                            if report.x_nt_id:
                                attachment_id = self.create_attachment(conn, report.x_nt_id, report_type_nt,
                                                                       sale_order_data[0])
                                attachment_ids.append(attachment_id)
                    message_id = self.create_message_post(conn, sale_order_data[0], attachment_ids)



