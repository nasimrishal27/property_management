# -*- coding: utf-8 -*-
from odoo import models,api


class RentalLeaseReport(models.AbstractModel):
    _name = 'report.property_management.report_rental_lease_report_details'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['rental.lease'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'rental.lease.pdf.report',
            'docs': docs,
            'data': data,
        }
