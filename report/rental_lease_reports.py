# -*- coding: utf-8 -*-
from odoo import models,api


class RentalLeaseReport(models.AbstractModel):
    _name = 'report.property_management.report_rental_lease_report_details'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_model': 'rental.lease.report.wizard',
            'data': data,
        }
