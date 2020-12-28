# odoo chain最简安装

my company is immartian2021

python odoo-bin -r odoo -w odoo -d immartian2021 -i base --stop-after-init  --without-demo true

    """ Initialize a database with for the ORM.

    This executes base/data/base_data.sql, creates the ir_module_categories
    (taken from each module descriptor file), and creates the ir_module_module
    and ir_model_data entries.

    """

115个表 -》 database
133个初始模块-》 ir_model

http://127.0.0.1:8069/web?#action=35&model=ir.module.module&view_type=kanban&cids=&menu_id=5

选择已安装，可以看到原始安装为8个模块

安装account,卸载partner_autocomplete，会只有39个models,默认安装了美国科目表

INSERT INTO "public"."res_currency" ("id", "name", "symbol", "rounding", "decimal_places", "active", "position", "currency_unit_label", "currency_subunit_label", "create_uid", "create_date", "write_uid", "write_date") VALUES ('7', 'CNY', '¥', '0.010000', '2', 't', 'before', 'Yuan', 'Fen', '1', '2020-12-12 18:34:54.670355', '1', '2020-12-18 17:37:07.712232');

主要的配置说明在odoo/tools/config.py

## 安装新模块

### 安装account,注意不要安装demo

python odoo-bin -r odoo -w odoo -d immartian2021 -i account  --addons-path=addons,odoo/addons,../addons_chain --stop-after-init  --without-demo true

python odoo-bin -r odoo -w odoo -d immartian2021 -i l10n_generic_coa  --addons-path=addons,odoo/addons,../addons_chain --stop-after-init  --without-demo true

### 安装chain_fbprophet

python odoo-bin -r odoo -w odoo -d immartian2021 -i chain_fbprophet  --addons-path=addons,odoo/addons,../addons_chain --stop-after-init  --without-demo true

更新：

python odoo-bin -r odoo -w odoo -d immartian2021 -u chain_fbprophet  --addons-path=addons,odoo/addons,../addons_chain --stop-after-init  --without-demo true


### 安装联系人

### 遇见model cache has been invalidated,安装

python odoo-bin -r odoo -w odoo -d immartian2021 -u ir_ui_view_cache_test  --addons-path=addons,odoo/addons,../odoo_saltfun/addons,../addons_chain --stop-after-init  --without-demo true

ir_ui_view_cache_test

## 问题

INSERT INTO "public"."ir_attachment" ("id", "name", "description", "res_model", "res_field", "res_id", "company_id", "type", "url", "public", "access_token", "db_datas", "store_fname", "file_size", "checksum", "mimetype", "index_content", "create_uid", "create_date", "write_uid", "write_date", "original_id") VALUES ('27', 'res.company.scss', NULL, NULL, NULL, NULL, '1', 'binary', '/web/static/src/scss/asset_styles_company_report.scss', NULL, NULL, NULL, '75/751da1e706f06a22e3b1345f9ee7f393450e0250', '687', '751da1e706f06a22e3b1345f9ee7f393450e0250', 'text/scss', '




                .o_company_1_layout {
                font-family: ''Lato'';
            
                &.o_report_layout_standard {
                    h2 {
                        color: black;
                    }
                    #informations strong {
                        color: black;
                    }
                    #total strong{
                        color: black;
                    }
                    table {
                        thead {
                            color: black;
                        }
                    }
                }
            
            }
        
    ', '1', '2020-12-19 20:24:53.71404', '1', '2020-12-19 20:24:53.71404', NULL);
