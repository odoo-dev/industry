{
    'name': 'Gardening',
    'version': '1.0',
    'category': 'Services',
    'description': """
This industry is ideal for gardening businesses proficient in managing projects from conception to completion,
focusing on accurate quoting, efficient planning, seamless execution, and excellent customer service, ...
""",
    'depends': [
        'crm_enterprise',
        'industry_fsm_stock',
        'industry_fsm',
        'knowledge',
        'purchase_stock',
        'sale_crm',
        'planning',  
    ],
    'data': [
        'data/hr_job.xml',
        'data/ir_attachment_pre.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/product_category.xml',
        'data/project_task_type.xml',
        'data/project_project.xml',
        'data/product_template.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/mail_message.xml',
        "data/knowledge_article_favorite.xml",
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/account_analytic_account.xml',
        'demo/hr_employee.xml',
        'demo/crm_lead.xml',
        'demo/sale_order.xml',
        'demo/sale_order_line.xml',
        'demo/sale_order_confirm.xml',
        'demo/project_project.xml',
        'demo/project_task.xml',
        'demo/product_supplierinfo.xml',
        'demo/product_product.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_line.xml',
        'demo/purchase_order_confirm.xml',
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
}
