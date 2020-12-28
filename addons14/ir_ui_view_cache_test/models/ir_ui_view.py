# -*- coding: utf-8 -*-


from odoo import api, models, tools, fields
from timeit import default_timer as timer

import logging
_logger = logging.getLogger(__name__)


class ViewCacheTest(models.Model):
    _name = 'ir.ui.view.cache.test'
    _description = 'Tests for ui view cache'
    _log_access = False


    access_time = fields.Datetime()

    generate_time = fields.Float(
        string='Generate Time (in seconds)',
        readonly=True,
    )



class View(models.Model):
    _inherit = 'ir.ui.view'

    # apply ormcache_context decorator unless in dev mode...
    @api.model
    @tools.conditional(
        'xml' not in tools.config['dev_mode'],
        tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'view_id',
                       'tuple(self._context.get(k) for k in self._read_template_keys())'),
    )
    
    def _read_template(self, view_id):
        if 'xml' in tools.config['dev_mode']:
            return super(View, self)._read_template(view_id)

        start = timer()
        res = super(View, self)._read_template(view_id)
        time = (timer() - start)
        try:
            self.env.cr.execute("insert into ir_ui_view_cache_test (access_time, generate_time) values(now() at time zone 'utc', %s)", (time, ))
        except Exception as e:
            _logger.exception(e)
        _logger.info('Probably would have saved {:f}ms'.format(time * 1000))

        return res
