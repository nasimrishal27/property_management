# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class PortalWebsite(http.Controller):
    @http.route('/property/', auth='public', website=True)
    def property(self, **kw):
        # return http.request.render('property_management.sample', {
        #     'teachers': ["Diana Padilla", "Jody Caroll", "Lester Vaughn"],
        # })
        property = http.request.env['property.property']
        return http.request.render('property_management.property', {
            'property': property.search([])
        })