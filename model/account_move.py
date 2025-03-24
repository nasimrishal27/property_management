# -*- coding: utf-8 -*-
from odoo import _, fields, models


class AccountMove(models.Model):
    """ model for Invoice """
    _inherit = 'account.move'

    rental_lease_id = fields.Many2one("rental.lease", string="Rental Lease")

    def action_post(self):
        """ Override invoice posting to log a message in rental.lease chatter """
        if self.rental_lease_id:
            message = _("Invoice %s has been posted for %s. Amount: %s", self.name,
                        self.rental_lease_id.name, self.amount_total)
            self.rental_lease_id.message_post(body=message, subtype_xmlid="mail.mt_note")
        return super().action_post()
