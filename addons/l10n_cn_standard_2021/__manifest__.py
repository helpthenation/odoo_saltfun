# -*- coding: utf-8 -*-

# Copyright (C) 2008-2008 凯源吕鑫 lvxin@gmail.com   <basic chart data>
#                         维智众源 oldrev@gmail.com  <states data>
# Copyright (C) 2012-2012 南京盈通 ccdos@intoerp.com <small business chart>
# Copyright (C) 2008-now  开阖软件 jeff@osbzr.com    < PM and LTS >
# Copyright (C) 2017-now  jeffery9@gmail.com
# Copyright (C) 2018-11  广州尚鹏 https://www.sunpop.cn
# Copyright (C) 2019-now  山东天骄 https://www.odoochain.cn

{
    'name': '2021最新中国企业会计表',
    'version': '14.0.0.0',
    'author': 'Odoochain.cn',
    'category': 'Accounting/Accounting',
    'website': 'https://www.Odoochain.cn',
    'license': 'LGPL-3',
    'sequence': 12,
    'summary': """    
    Multi level account chart. Chinese enhance. Focus on account chart.
    Add account chart group data. Account group, Chinese tax.
    Set chinese account report. 
    """,
    'description': """
    2021中国化财务，主要针对标准会计科目表作了优化。
    1. 使用用友Yonyou的会计科目命名法对多级科目进行初始化,可自行调整为金蝶科目命名法
    """,
    'depends': [
        'account',
    ],
    'images': ['static/description/banner.png'],
    'data': [
        'views/account_account_views.xml',
        'views/account_views.xml',
        'data/chart_data.xml',
        'data/account_account_tag_data.xml',
        'data/account.group.csv',
        'data/account.account.template.csv',
        'data/account_tax_group_data.xml',
        'data/account_tax_template_data.xml',
        'data/account_chart_template_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
