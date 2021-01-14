## first install base 

下面这样做的好处是不安装demo，只初始化base

python odoo-bin -r odoo -w odoo -d odoo13 -i base --addons-path=addons,odoo/addons --stop-after-init --without-demo all

## RUN 修改默认端口，因为本地运行多个odoochain

根据自身情况修改添加addons位置：
```angular2html
python odoo-bin -r odoo -w odoo -D ../odoo13data -d odoo13 --http-port 8079 --dev all --load-language zh_CN --addons-path=addons,odoo/addons,../addons_saltfun/addons13,../addons_chain/addons13
```
-i https://pypi.doubanio.com/simple