# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RentalLeasePdfReport(models.Model):
    """ model for storing rental/lease details """
    _name = "rental.lease.pdf.report"
    _description = "Rental/Lease Management PDF Report"

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    state = fields.Selection([("draft", "Draft"), ("to-approve", "To Approve"),
                              ("confirm", "Confirmed"), ("close", "Closed"), ("return", "Returned"),
                              ("expired", "Expired")])
    tenant_id = fields.Many2one(comodel_name="res.partner", string="Tenant")
    owner_id = fields.Many2one(comodel_name='res.partner', string="Owner")
    property_type = fields.Selection([("rent", "Rent"), ("lease", "Lease")], string="Type")
    property_id = fields.Many2one(comodel_name='property.property', string="Property")

    def action_print_pdf(self):
        """df"""
        print('Haiii')
        # tenant = self.tenant_id.ensure_one()
        # query = """
        #             SELECT *
        #             FROM rental_lease
        #             WHERE tenant_id = %s
        #         """
        # params = (self.tenant_id.id,)
        # self.env.cr.execute(query, params)
        # report = self.env.cr.dictfetchall()
        #
        # data = {
        #     'tenant_id': tenant.name,
        #     # 'filter_by': self.filter_by,
        #     # 'date_from': self.date_from,
        #     # 'date_to': self.date_to,
        #     'report': report,
        # }
        # return self.env.ref('property_management.action_rental_lease_request_report').report_action(self, data=data)
        query = """SELECT name,total_amount,type,state
                    FROM rental_lease
                    WHERE tenant_id = '%s'""" % self.tenant_id.id
        # if self.from_date:
        #     query += """ where tb.date >= '%s' and tb.date <= '%s'""" % self.from_date, %self.to_date
        self.env.cr.execute(query)
        report = self.env.cr.dictfetchall()
        # data = {'company_id': self.env.user.company_id.id, 'report': report}
        print(report)
        data = {'tenant_id': self.tenant_id.id, 'report': report}
        return self.env.ref('property_management.action_rental_lease_request_report').report_action(None, data=data)

    def action_back(self):
        """User rejects the transfer and returns to editing."""
        return {'type': 'ir.actions.act_window_close'}
