# -*- coding: utf-8 -*-
from odoo import fields, models


class RentalLeasePdfReport(models.TransientModel):
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
        """Function for printing report"""
        query = """SELECT r.name,p.name as partner,r.total_amount,r.property_type,r.state
                    FROM rental_lease r join res_partner p on tenant_id = p.id
                    join rental_lease_order_line l on l.order_id = r.id
                    join property_property pr on l.property_id = pr.id"""
        where_clause = ["r.company_id = %s" % self.env.company.id]
        if self.from_date:
            where_clause.append("date_start >= '%s'" % self.from_date)
        if self.to_date:
            where_clause.append("date_end <= '%s'" % self.to_date)
        if self.state:
            where_clause.append("state = '%s'" % self.state)
        if self.tenant_id:
            where_clause.append("tenant_id = %s" % self.tenant_id.id)
        if self.owner_id:
            where_clause.append("owner_id = %s" % self.owner_id.id)
        if self.property_type:
            where_clause.append("property_type = '%s'" % self.property_type)
        if self.property_id:
            where_clause.append("property_id = %s" % self.property_id.id)
        if where_clause:
            query += " WHERE " + " AND ".join(where_clause)
        self.env.cr.execute(query)
        report = self.env.cr.dictfetchall()
        data = {'report': report}
        return self.env.ref('property_management.action_rental_lease_request_report').report_action(None, data=data)

    def action_back(self):
        """cancel button"""
        return {'type': 'ir.actions.act_window_close'}
