{
    'name': 'Custom Image Upload eCommerce',
    'version': '1.0',
    'category': 'Product',
    'summary': 'Adds Allow Image Uploads through eCommerce',
    'depends': ['base', 'sale_management', 'website_sale'],
    'license': 'OPL-1',
    'data': [
        'data/ir_model_fields.xml',
        'data/store_custom_image.xml',
        'views/product_template_views.xml',
        'views/upload_image_button.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'image_upload_ecommerce/static/src/js/website_sale.js',
        ]
    },
    'installable': True,
    'application': False,
}