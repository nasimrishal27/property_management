# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RentalLeaseOrderLine(models.Model):
    """ Model for Rental/Lease order line """
    _name = "rental.lease.order.line"
    _description = "Rental Lease Order Line"

    order_id = fields.Many2one(comodel_name='rental.lease', string="Order Reference", required=True,
                               ondelete='cascade', copy=False)
    company_id = fields.Many2one(related='order_id.company_id', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True)
    property_id = fields.Many2one(comodel_name='property.property', string="Property",
                                  domain=[('state', '=', 'draft')])
    price_unit = fields.Monetary(string="Property Price", compute="_compute_amount")
    price_subtotal = fields.Monetary(string="Subtotal", compute='_compute_subtotal')
    invoice_line_ids = fields.Many2many(comodel_name='account.move.line',
                                        relation='rental_lease_order_line_invoice_rel',
                                        column1='order_line_id', column2='invoice_line_id')
    order_partner_id = fields.Many2one(related='order_id.tenant_id', string="Customer", store=True)
    state = fields.Selection(related='order_id.state', string="Order Status", store=True)
    qty_invoiced = fields.Float(string="Invoiced Quantity", compute='_compute_qty_invoiced',
                                store=True)
    quantity = fields.Float(string="Quantity", digits='Product Unit of Measure', store=True)
    qty_to_invoice = fields.Float(string="Quantity to Invoice")

    @api.depends('order_id.property_type', 'property_id', 'order_id.total_days')
    def _compute_amount(self):
        """ Computing amount """
        for rec in self:
            rec.quantity = rec.order_id.total_days
            rec.qty_to_invoice = rec.order_id.total_days
            if rec.order_id.property_type == 'rent':
                rec.price_unit = rec.property_id.rent_amount
            else:
                rec.price_unit = rec.property_id.lease_amount

    @api.depends('price_unit', 'order_id.total_days')
    def _compute_subtotal(self):
        """ Calculate Subtotal Amount """
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.order_id.total_days
            if rec.order_id.property_type == 'rent':
                rec.property_id.rent_amount = rec.price_unit
            else:
                rec.property_id.lease_amount = rec.price_unit

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.move_id.state')
    def _compute_qty_invoiced(self):
        """ Calculate Invoiced Quantity """
        for line in self:
            total_qty = sum(
                invoice_line.quantity
                for invoice_line in line.invoice_line_ids
                if invoice_line.move_id.state != 'cancel'
            )
            line.qty_invoiced = total_qty
            line.qty_to_invoice = max(line.quantity - line.qty_invoiced, 0)
