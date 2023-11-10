# -*- coding: utf-8 -*-
{
    'name': 'Commodity Trading',
    'version': '1.0',
    'category': 'industry',
    'description': """
        Tailored for commodity traders (e.g., soybeans, wheat) with comprehensive functions,
        including CRM, quality checks, and broker involvement for product quality and commissions.
    """,
    'author': 'Odoo S.A.',
    'depends': [
        'account_edi_ubl_cii',
        'account_followup',
        'appointment_crm',
        'knowledge',
        'mrp_account',
        'product_expiry',
        'product_images',
        'purchase_mrp',
        'quality_control_worksheet',
        'quality_mrp',
        'quality_mrp_workorder',
        'sale_crm',
        'sale_mrp',
        'sale_planning',
        'sale_product_configurator',
        'sale_project',
        'stock_dropshipping',
        'stock_picking_batch',
        'website_appointment',
        'website_crm',
        'website_crm_partner_assign',
    ],
    'data': [
        'data/res_config_settings.xml',
        'data/ir_attachment_pre.xml',
        'data/ir_sequence.xml',
        'data/ir_model.xml',
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_actions_report.xml',
        'data/ir_ui_menu.xml',
        'data/ir_model_access.xml',
        'data/ir_rule.xml',
        'data/product_category.xml',
        'data/worksheet_template.xml',
        'data/product_template.xml',
        'data/product_product.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_member.xml',
        'data/quality_point.xml',
        'data/mrp_bom.xml',
        'data/mrp_bom_line.xml',
        'data/mrp_workcenter.xml',
        'data/mrp_routing_workcenter.xml',
    ],
    'demo': [
        'demo/weighing_scale_maste.xml',
        'demo/res_partner.xml',
        'demo/product_supplierinfo.xml',
        'demo/stock_lot.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_post.xml',
        'demo/mrp_production.xml',
        'demo/mrp_production_post.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_post.xml',
    ],
    'application': False,
    'license': 'OPL-1',
}
