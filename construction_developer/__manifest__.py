{
    'name': 'Construction Developer',
    'version': '2.0',
    'category': 'Construction',
    'depends': [
        'base_industry_data',
        'construction',
        'mrp',
        'web_gantt',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/stock_location.xml',

        'features/remarks/remark.xml',
        'features/remarks/remark_category.xml',
        'features/remarks/remark_stage.xml',
        'features/remarks/remark_views_and_actions.xml',
        'data/x_remark_category.xml',
        'data/x_remark_stage.xml',

        'features/sol_numbering.xml',
        'features/work_items/create_worksite_loc_on_so_confirm.xml',
        'features/work_items/route_configs.xml',
        'features/work_items/link_mrp_loc_bom_on_so_confirm.xml',
        'features/work_items/product_bom_template_and_routes.xml',
        'features/work_items/bom_margin.xml',
        'features/work_items/access_bom_from_so.xml',
        'features/work_items/check_so_bom_price_updates.xml',
        'features/work_items/open_stock_from_so.xml',
        'features/work_items/link_picking_loc_on_po_confirm.xml',
        'features/work_items/delivery_progress/delivery_progress.xml',
        'features/work_items/delivery_progress/report.xml',
        'features/work_items/delivery_progress/templates.xml',
        'features/work_items/work_breakdown_structure.xml',


        'features/work_items/cost_nature/cost_nature.xml',
        'data/product_category.xml',

        'features/work_items/cost_nature/report.xml',

        'security/ir_access.xml',
        'data/views_standard.xml',
        'data/qweb_view.xml',
    ],
    'demo': [
        'demo/stock_location.xml',
        'demo/res_company.xml',
        'demo/res_partner.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_developer/static/src/js/mail_chatter.xml',
        ],
        'web.assets_backend_lazy': [
            'construction_developer/static/src/js/patch.js',  # web_gantt/gantt_renderer is lazy so this needs to be lazy too
        ],
    },
    'cloc_exclude': [
        'data/qweb_view.xml',
        'features/work_items/delivery_progress/templates.xml',
        'static/src/js/mail_chatter.xml',
    ],
    'images': ['images/main.png'],
    'license': 'OEEL-1',
    'application': True,
    'author': 'Odoo S.A.',
    'url': "https://www.odoo.com/trial?industry&selected_app=construction_developer",
    'website': "https://www.odoo.com/all-industries",
}
