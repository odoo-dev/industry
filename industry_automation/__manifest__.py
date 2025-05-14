{
    'name': 'Industry Automation',
    'version': '1.0',
    'summary': 'Industry Automation Cleanup',
    'author': 'chirag Gami(chga)',
    'category': 'Automation',
    'depends': ['base', 'project', 'sale_management'],
    'license': 'LGPL-3',
    'data': [
        'views/project_task_views.xml',
        'data/fetch_db_cron.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}