# -*- coding: utf-8 -*-
from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class RentalLease(models.Model):
    """ model for storing rental/lease details """
    _name = "rental.lease"
    _description = "Rental or Lease Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name desc"

    name = fields.Char(string="Sequence", copy=False, default=lambda self: _('New'),
                       readonly=True)
    tenant_id = fields.Many2one(comodel_name="res.partner", string="Tenant",
                                required=True)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='Expiration Date', tracking=True, required=True)
    total_days = fields.Integer(string="Total Days", compute="_compute_total_days", store=True)
    state = fields.Selection([("draft", "Draft"), ("to-approve", "To Approve"),
                              ("confirm", "Confirmed"), ("close", "Closed"), ("return", "Return"),
                              ("expired", "Expired")], default="draft", tracking=True)
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=lambda self: self.env.user.company_id.id)
    property_type = fields.Selection([("rent", "Rent"), ("lease", "Lease")], string="Type",
                                     required=True, default="rent")
    invoice_count = fields.Integer(string="Invoice", compute='_compute_invoice_count', store=True)
    order_line_ids = fields.One2many(comodel_name='rental.lease.order.line',
                                     inverse_name='order_id', ondelete='cascade')
    amount_paid = fields.Integer(string="Amount Paid", compute='_compute_amount_paid', store=True)
    payment_state = fields.Selection(selection=[('draft', 'Draft'), ('not_paid', 'Not Paid'),
                                                ('paid', 'Paid'), ('partial', 'Partial')],
                                     string="Payment Status", store=True, default='draft')
    amount_due = fields.Integer(string="Amount Due")

    @api.depends('order_line_ids.property_id', 'property_type', 'total_days')
    def _compute_total_amount(self):
        """ Total Amount """
        for order in self:
            order.total_amount = sum(order.order_line_ids.mapped('price_subtotal'))

    @api.depends('order_line_ids.invoice_line_ids.move_id')
    def _compute_invoice_count(self):
        """ Invoice Count """
        for record in self:
            record.invoice_count = (self.env['account.move'].search_count([
                ("id", "=", self.order_line_ids.invoice_line_ids.move_id.ids)]))

    @api.depends('invoice_count', 'order_line_ids.invoice_line_ids.move_id.payment_state')
    def _compute_amount_paid(self):
        """Calculate the total amount paid for the rental order"""
        for record in self:
            invoices = self.env["account.move"].search([
                ("id", "=", self.order_line_ids.invoice_line_ids.move_id.ids),
                ("state", "=", "posted")])
            record.amount_paid = sum(invoice.amount_total for invoice in invoices
                                     if invoice.payment_state == 'paid')
            record.amount_due = max(record.total_amount - record.amount_paid, 0)
            if record.amount_paid == 0:
                record.payment_state = 'not_paid'
            elif record.amount_paid < record.total_amount:
                record.payment_state = 'partial'
            else:
                record.payment_state = 'paid'

    @api.depends('date_end', 'date_start')
    def _compute_total_days(self):
        """ Calculate total no of days """
        for rec in self:
            if rec.date_end:
                rec.total_days = (rec.date_end - rec.date_start).days

    @api.model
    def create(self, vals):
        """ Create a sequence for the model """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('rental.lease')
        return super().create(vals)

    def action_create_invoice(self):
        """ Method to create invoice """
        self.ensure_one()
        invoice_obj = self.env["account.move"]
        invoice_line_obj = self.env["account.move.line"]
        invocable_lines = self.order_line_ids.filtered(lambda l: l.qty_to_invoice > 0)

        if not invocable_lines:
            raise UserError("There is no quantity to invoice for this order.")

        draft_invoice = self.order_line_ids.invoice_line_ids.move_id.filtered(
            lambda l: l.state == 'draft')
        if draft_invoice:
            for line in invocable_lines:
                existing_line = line.invoice_line_ids.filtered(
                    lambda l: l.move_id.id == draft_invoice.id)
                if existing_line:
                    existing_line.write({"quantity": existing_line.quantity + line.qty_to_invoice})
                    line.invoice_line_ids = [fields.Command.link(existing_line.id)]
                else:
                    new_invoice_line = invoice_line_obj.create({
                        "move_id": draft_invoice.id,
                        "name": f"Rent for {line.property_id.name}",
                        "quantity": line.qty_to_invoice,
                        "price_unit": line.price_unit})
                    line.invoice_line_ids = [fields.Command.link(new_invoice_line.id)]

            invoice_id = draft_invoice.id
        else:
            new_invoice = invoice_obj.create({
                "partner_id": self.tenant_id.id,
                "move_type": "out_invoice",
                "invoice_origin": self.name})

            invoice_lines = []
            for line in invocable_lines:
                new_invoice_line = invoice_line_obj.create({
                    "move_id": new_invoice.id,
                    "name": f"Rent for {line.property_id.name}",
                    "quantity": line.qty_to_invoice,
                    "price_unit": line.price_unit})
                line.invoice_line_ids = [fields.Command.link(new_invoice_line.id)]
                invoice_lines.append(new_invoice_line.id)

            new_invoice.write({"invoice_line_ids": [fields.Command.set(invoice_lines)]})
            invoice_id = new_invoice.id
        return {
            "name": "Customer Invoice",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice_id,
            "target": "current",
        }

    def action_draft(self):
        """ draft button """
        self.write({'state': "draft"})
        self.order_line_ids.mapped('property_id').write({'state': 'draft'})

    def action_confirm(self):
        """ confirm button """
        if self.message_attachment_count < 1:
            raise ValidationError("Please Attachment The Supporting File")
        if self.env.user.has_group('property_management.property_management_group_manager'):
            self.write({'state': "confirm"})
            template = self.env['mail.template'].browse(
                self.env.ref('property_management.mail_template_rental_lease_order').id)
            if template:
                self.message_post_with_source(template, message_type='comment',
                                              subtype_xmlid='mail.mt_note')
            else:
                raise UserError("Mail Template not found. Please check the template.")
        else:
            self.write({'state': "to-approve"})
        if self.property_type == 'rent':
            self.order_line_ids.mapped('property_id').write({'state': 'rented'})
        elif self.property_type == 'lease':
            self.order_line_ids.mapped('property_id').write({'state': 'leased'})

    def action_approve(self):
        """ approve button """
        self.action_confirm()

    def action_close(self):
        """ close button """
        self.write({'state': "close"})
        self.order_line_ids.mapped('property_id').write({'state': 'draft'})
        template = self.env['mail.template'].browse(
            self.env.ref('property_management.mail_template_rental_lease_closed').id)
        if template:
            self.message_post_with_source(template, message_type='comment',
                                          subtype_xmlid='mail.mt_note')
        else:
            raise UserError("Mail Template not found. Please check the template.")

    def action_return(self):
        """ return button """
        self.write({'state': "return"})
        self.order_line_ids.mapped('property_id').write({'state': 'draft'})

    def action_expired(self):
        """ expire button """
        self.write({'state': "expired"})
        self.order_line_ids.mapped('property_id').write({'state': 'draft'})
        template = self.env['mail.template'].browse(
            self.env.ref('property_management.mail_template_rental_lease_expiry').id)
        if template:
            self.message_post_with_source(template, message_type='comment',
                                          subtype_xmlid='mail.mt_note')
        else:
            raise UserError("Mail Template not found. Please check the template.")

    def action_open_rental_lease_invoice(self):
        """ Smart Button Action """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'list, form',
            'views': [(False, 'list'), (False, 'form')],
            'res_model': 'account.move',
            'target': "current",
            'domain': [("id", "=", self.order_line_ids.invoice_line_ids.move_id.ids)]
        }

    def _cron_update_state(self):
        """ Update state to expired"""
        for rec in self.search([('state', '!=', 'expired')]).filtered(lambda l:
                                                                      l.date_end < date.today()):
            rec.action_expired()

    def _cron_payment_follow_up(self):
        """ Update state to expired"""
        for rec in self.search([('state', '=', 'expired')]).filtered(lambda l: l.amount_due > 0):
            template = rec.env['mail.template'].browse(
                rec.env.ref('property_management.mail_template_rent_lease_late_payment').id)
            self.message_post_with_source(template, message_type='comment',
                                          subtype_xmlid='mail.mt_note')
