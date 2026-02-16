{
    'name': 'Hotel Industry Website',
    'description': 'Custom website module for hotel industry',
    'version': '19.0.1.0.0',
    'author': 'PSBE DESIGN',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_sale',
        'website_sale_renting',
        'product',
        'delivery',
    ],
    'data': [
        'data/presets.xml',
        'data/website.xml',
        'data/images.xml',
        'data/menu.xml',
        'data/pages/contactus.xml',
        'data/pages/home.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'website_hotel/static/src/scss/primary_variables.scss',
        ],
    },
}
