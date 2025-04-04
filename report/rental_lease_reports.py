from odoo import models,api


class RentalLeaseReport(models.AbstractModel):
    _name = 'report.property_management.report_rental_lease_report_details'

    @api.model
    def _get_report_values(self, docids, data=None):
        domain = []
        if data.get('tenant_id'):
            domain.append(('tenant_id', '=', data.get('tenant_id')))
        docs = self.env['rental.lease'].search(domain)
        return {
            'doc_ids': docids,
            'doc_model': 'rental.lease.pdf.report',
            'docs': docs,
            'data': data,
        }
