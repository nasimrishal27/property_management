# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PropertyProperty(models.Model):
    """ model for storing property details """
    _name = "property.property"
    _description = "Property"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True)
    street = fields.Char(string="Street", required=True)
    street2 = fields.Char(string="street 2")
    zip = fields.Char(string="Zip Code", required=True)
    city = fields.Char(string="City", required=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               required=True, domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                 required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    country_code = fields.Char(related='country_id.code', string="Country Code")
    image = fields.Image(string="Image")
    date = fields.Date(string="Built Date", required=True)
    can_sold = fields.Boolean(default=False, string="Can Be Sold")
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    lease_amount = fields.Monetary(string="Lease Amount", required=True)
    rent_amount = fields.Monetary(string="Rent Amount", required=True)
    owner_id = fields.Many2one(comodel_name='res.partner', string="Owner")
    state = fields.Selection([('draft', 'Draft'), ('rented', 'Rented'), ('leased', 'Leased'),
                              ('sold', 'Sold')], default='draft', tracking=1)
    description = fields.Text(string="Description")
    record_count = fields.Integer(string="Rental/Lease", compute='_compute_record_count', default=0)
    facilities_ids = fields.Many2many(
        'property.facilities', 'property_facilities_rel', 'property_id',
        'facilities_id')
    active = fields.Boolean('Active', default=True,
                            help="If unchecked, it will archive property without removing it.")

    @api.depends('state')
    def _compute_record_count(self):
        """ Record Count """
        for record in self:
            record.record_count = self.env['rental.lease.order.line'].search_count([
                ('property_id', '=', self.id)])

    def action_open_rental_lease_record(self):
        """ Smart Button Action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rental/Lease',
            'view_mode': 'list, form',
            'views': [(False, 'list'), (False, 'form')],
            'res_model': 'rental.lease',
            'target': "current",
            'domain': [('order_line_ids.property_id', '=', self.id)]
        }

    def unlink(self):
        for record in self:
            record.env['rental.lease'].search([]).mapped("order_line_ids").filtered(
                lambda l: l.property_id == record).unlink()
            record.env['rental.lease'].search([]).filtered(lambda l: not l.order_line_ids).unlink()
        return super().unlink()
