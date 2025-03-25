# -*- coding: utf-8 -*-
{
    'name': "Property Management",
    'version': '1.0',
    'depends': ['base', 'contacts', 'account', 'mail', 'hr'],
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

        'views/property_facilities_view.xml',
        'views/property_property_view.xml',
        'views/rental_lease_order_line_view.xml',
        'views/rental_lease_view.xml',
        'views/res_partner.xml',
        'views/property_search_view.xml',
        'views/property_menu_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

