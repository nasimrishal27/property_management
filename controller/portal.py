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

    @http.route('/get/property/amount', type='json', auth='public')
    def get_property_rent_amount(self, property_id, property_type):
        property = http.request.env['property.property'].sudo().browse(property_id)
        amount = 0
        print(property_type)
        if property_type == 'rent':
            amount = property.rent_amount
        elif property_type == 'lease':
            amount = property.lease_amount
        return {
            'amount': amount
        }

    @http.route('/property-shop/submit', type='http', auth='public', website=True, methods=['POST'])
    def web_form_submit(self, **post):
        print(post)
        http.request.env['rental.lease'].sudo().create({
            'tenant_id': http.request.env.user.partner_id.id,
            'date_start': post.get('from_date'),
            'date_end': post.get('to_date'),
            'property_type': post.get('property_type'),
        })
        return http.request.render('property_management.property_shop')