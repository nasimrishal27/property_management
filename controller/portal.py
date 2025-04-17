# -*- coding: utf-8 -*-
import json
from odoo import http


class PortalWebsite(http.Controller):
    @http.route('/property-shop', auth='public', website=True)
    def property_shop(self, **kw):
        property_id = http.request.env['property.property'].search([('state', '=', 'draft')])
        return http.request.render('property_management.property_shop', {
            'property_id': property_id
        })
