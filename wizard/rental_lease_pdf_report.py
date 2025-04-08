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
    tenant_ids = fields.Many2many(comodel_name="res.partner", string="Tenant")
    owner_ids = fields.Many2many(comodel_name='res.partner', string="Owner",
                                 relation="res_partner_rental_lease_pdf_report_owner_id_rel")
    property_type = fields.Selection([("rent", "Rent"), ("lease", "Lease")], string="Type")
    property_ids = fields.Many2many(comodel_name='property.property', string="Property")

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
            where_clause.append("r.state = '%s'" % self.state)
        if self.tenant_ids:
            where_clause.append("tenant_id in (%s)" % str(self.tenant_ids.ids)[1:-1])
        if self.owner_ids:
            where_clause.append("owner_id in (%s)" % str(self.owner_ids.ids)[1:-1])
        if self.property_type:
            where_clause.append("property_type = '%s'" % self.property_type)
        if self.property_ids:
            where_clause.append("property_id in (%s)" % str(self.property_ids.ids)[1:-1])
        if where_clause:
            query += " WHERE " + " AND ".join(where_clause)
        self.env.cr.execute(query)
        report = self.env.cr.dictfetchall()
        data = {'report': report}
        return self.env.ref('property_management.action_rental_lease_request_report').report_action(None, data=data)
