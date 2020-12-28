## first install base 

python odoo-bin -r odoo -w odoo -d odoo13 -i base --addons-path=addons,odoo/addons --stop-after-init --without-demo all

## RUN 修改默认端口，因为本地运行多个odoochain

python odoo-bin -r odoo -w odoo -d odoo13 --http-port 8079 --dev all --addons-path=addons,odoo/addons,../odoo_saltfun/addons13,../addons_chain13 --load-language zh_CN