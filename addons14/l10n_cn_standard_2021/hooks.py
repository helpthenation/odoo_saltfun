# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

def pre_init_hook(cr):
    """
    数据初始化，只在安装时执行，更新时不执行
    """
    pass


def post_init_hook(cr, registry):
    """
    数据初始化，只在安装后执行，更新时不执行
    此处不执行，只是记录，该数据已处理完成
    """
    # cr.execute("UPDATE account_account_template set group_id = "
    #            "(select id from account_group where account_group.code_prefix_start=trim(substring(account_account_template.code from 1 for 1)) limit 1);")

    cr.execute("UPDATE account_account set group_id = "
               "(select id from account_group where account_group.code_prefix_start=trim(substring(account_account.code from 1 for 1)) limit 1);")
    cr.commit()
    pass

