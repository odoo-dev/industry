{
    'name': 'Bookstore',
    'version': '1.0',
    'category': 'Retail',
    'description': """
""",
    'depends': [
        'account_followup',
        'contacts',
        'knowledge',
        'loyalty',
        'point_of_sale',
        'pos_discount',
        'pos_sale',
        'purchase_stock',
        'sale_management',
        'sale_purchase',
        'stock_account',
        'stock_barcode_barcodelookup',
        'web_studio',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/base_automation.xml',
        'data/ir_actions_server.xml',
        'data/ir_default.xml',
        'data/pos_category.xml',
        'data/product_category.xml',
        'data/product_pricelist.xml',
        'data/product_product.xml',
        'data/pos_payment_method.xml',
        'data/pos_config.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/mail_message.xml',
        'data/knowledge_tour.xml',
        'data/customer_order_tour.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/product_supplierinfo.xml',
        'demo/loyalty_program.xml',
        'demo/loyalty_rule.xml',
        'demo/loyalty_reward.xml',
        'demo/loyalty_card.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/stock_warehouse_orderpoint.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_confirm.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bookstore/static/src/js/my_tour.js',
            'bookstore/static/src/js/tours/customer_order_tour.js',
        ]
    },
    "cloc_exclude": [
        "data/knowledge_article.xml",
        "static/src/js/my_tour.js",
        "static/src/js/tours/customer_order_tour.js",
    ],
    'license': 'OPL-1',
    'author': 'Odoo S.A.',
    'images': ['images/main.png'],
}
