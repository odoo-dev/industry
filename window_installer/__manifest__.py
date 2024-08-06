{
    'name': 'Window Installation',
    'version': '1.0',
    'category': 'Services',
    'description': """
This industry is ideal for window installation businesses proficient in managing projects from conception to completion,
focusing on accurate quoting, efficient planning, seamless execution, and excellent customer service, ...
""",
    'depends': [
        'crm_enterprise',
        'documents',
        'helpdesk',
        'hr_fleet',
        'knowledge',
        'maintenance',
        'purchase_stock',
        'sale_crm',
        'sign',
        'mrp',
    ],
    'data': [
        'data/documents_folder.xml',
        'data/stock_location.xml',
        'data/ir_attachment_pre.xml',
        'data/knowledge_cover.xml',
        'data/knowledge_article.xml',
        'data/knowledge_article_favorite.xml',
        'data/project_task_type.xml',
        'data/product_category.xml',
        'data/project_project.xml',
        'data/product_template.xml',
        'data/mail_message.xml',
        'data/product_attribute.xml',
        'data/product_attribute_value.xml',
        'data/product_template_attribute_line.xml',
        'data/product_template_attribute_value.xml',
        'data/product_product.xml',
        'data/hr_job.xml',
    ],
    'demo': [
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/fleet_cars_data.xml',
        'demo/fleet_vehicle.xml',
        'demo/account_analytic_account.xml',
        'demo/crm_lead.xml',
        'demo/sale_order.xml',
        'demo/sale_order_confirm.xml',
        'demo/sale_order_line.xml',
        'demo/project_task.xml',
        'demo/planning_recurrency.xml',
        'demo/planning_slot.xml',
        'demo/purchase_order.xml',
        'demo/purchase_order_confirm.xml',
        'demo/purchase_order_line.xml',
        'demo/product_supplierinfo.xml',
    ],
    'license': 'OPL-1',
    'images': ['images/main.png'],
}
