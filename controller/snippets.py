from odoo import http
from odoo.http import request

class WebsiteProduct(http.Controller):
    @http.route('/get_latest_properties', auth="public", type='json', website=True)
    def get_latest_property(self):
        """Get the latest property for the snippet."""
        latest_property = request.env['property.property'].sudo().search_read(
            [('active', '=', True)], fields=['name', 'image', 'id', 'rent_amount', 'lease_amount'], order='create_date desc'
        )
        values = {
            'properties': latest_property,
        }
        return values

    @http.route('/get_latest_properties/<int:property_id>', auth="public", type='http', website=True)
    def get_latest_property_details(self, property_id):
        """Get the latest property details."""
        property = request.env['property.property'].sudo().browse(property_id)
        return http.request.render('property_management.property_details', {
            'property': property,
        })