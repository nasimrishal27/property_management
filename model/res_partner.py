# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    """ Partner Model """
    _inherit = "res.partner"

    rental_lease_count = fields.Integer(string="Rental/Lease", compute='_compute_rental_lease_count', default=0)

    def _compute_rental_lease_count(self):
        """ Record Count """
        for record in self:
            record.rental_lease_count = self.env['rental.lease'].search_count([('tenant_id', '=', self.id)])

    def action_open_rental_lease(self):
        """ Smart Button Action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rental/Lease',
            'view_mode': 'list, form',
            'views': [(False, 'list'), (False, 'form')],
            'res_model': 'rental.lease',
            'target': "current",
            'domain': [('tenant_id', '=', self.id)]
        }
