# -*- coding: utf-8 -*-
from odoo import fields
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalWebsite(http.Controller):
    """ Website portal """

    @http.route('/property-shop', auth='public', website=True)
    def property_shop(self):
        """ Rendering property-shop page"""
        property_id = http.request.env['property.property'].search([('state', '=', 'draft')])
        return http.request.render('property_management.property_shop', {
            'property_id': property_id,
        })

    @http.route('/get/property/amount', type='json', auth='public')
    def get_property_rent_amount(self, property_id, property_type):
        """Fetching the price_unit from DB"""
        property = http.request.env['property.property'].sudo().browse(property_id)
        amount = 0
        if property_type == 'rent':
            amount = property.rent_amount
        elif property_type == 'lease':
            amount = property.lease_amount
        return {
            'amount': amount
        }

    @http.route('/property-shop/submit', type='json', auth='user', website=True)
    def web_form_submit(self, data, user_data):
        """ Creating order from website """
        http.request.env['rental.lease'].sudo().create({
            'tenant_id': http.request.env.user.partner_id.id,
            'date_start': user_data[0].get('from_date'),
            'date_end': user_data[0].get('to_date'),
            'property_type': user_data[0].get('type'),
            'order_line_ids': [fields.Command.create({'property_id': int(rec['property'])})
                               for rec in data]
        })
        return True

    @http.route('/my/rental-lease-orders', auth='user', website=True)
    def rental_lease_orders(self):
        """ Rendering order list page"""
        partner = http.request.env.user.partner_id
        order_ids = http.request.env['rental.lease'].sudo().search([('tenant_id', '=', partner.id)])
        values = {
            'order_ids': order_ids,
            'page_name': 'order-ids',
        }
        return http.request.render('property_management.rental_lease_orders', values)

    @http.route('/my/rental-lease-orders/<int:order_id>/', auth='user', website=True)
    def rental_lease_order(self, order_id):
        """ Rendering order preview page"""
        order = http.request.env['rental.lease'].sudo().browse(order_id)

        values = {
            'rental_lease_order': order,
            'page_name': 'rental-lease-order',
        }
        return http.request.render('property_management.rental_lease_order_portal_template', values)

    @http.route('/property-shop/success', auth='public', website=True)
    def order_success(self):
        """ Rendering thankyou page"""
        return http.request.render('property_management.property_thankyou')


class RentalPortalAccount(CustomerPortal):
    """ Adding menu to the portal """

    def _prepare_home_portal_values(self, counters):
        """ Counting the total order"""
        values = super()._prepare_home_portal_values(counters)
        if 'rental_lease_count' in counters:
            rental_lease_count = http.request.env['rental.lease'].sudo().search_count(
                [('tenant_id', '=', http.request.env.user.partner_id.id)])
            values['rental_lease_count'] = rental_lease_count
        return values
