{
    'name': 'Hotel Industry Website',
    'description': 'Custom website module for hotel industry',
    "category": "Theme/Retail",
    "summary": "Hotel, Rooms, Booking",
    'version': '19.0.1.0.0',
    'author': 'PSBE DESIGN',
    'license': 'OEEL-1',
    "images": [
        "static/description/hotel_screenshot.jpg",
    ],
    'depends': [
        'website',
        'website_sale',
        'website_sale_renting',
        'product',
        'delivery',
    ],
    'data': [
        'data/website.xml',
        'data/server_actions.xml',
        'data/images.xml',
        'data/menu.xml',
        'data/pages/contactus.xml',
        'data/pages/home.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'theme_hotel/static/src/scss/primary_variables.scss',
        ],
    },
}
