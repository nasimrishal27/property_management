# -*- coding: utf-8 -*-
{
    'name': "Property Management",
    'version': '1.0',
    'depends': ['base', 'contacts', 'account', 'mail', 'hr', 'website', 'web'],
    'sequence': 1,
    'author': "Suni",
    'category': 'All',
    'description': """
    Property Management
    """,
    # data files always loaded at installation
    'data': [
        'security/property_groups.xml',
        'security/property_security.xml',
        'security/ir.model.access.csv',

        'data/property_demo.xml',
        'data/property_facilities_demo.xml',
        'data/ir_sequence.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'data/paper_format_demo.xml',
        'data/property_management_portal_templates.xml',
        'data/website_menu.xml',

        'views/property_facilities_view.xml',
        'views/property_property_view.xml',
        'views/rental_lease_view.xml',
        'views/res_partner.xml',
        'views/property_search_view.xml',
        'views/property_menu_view.xml',

        'report/rental_lease_reports_templates.xml',
        'report/rental_lease_reports.xml',

        'wizard/rental_lease_report_wizard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
                'property_management/static/src/js/action_manager.js',
            ],
        'web.assets_frontend': [
            'property_management/static/src/js/portal.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

