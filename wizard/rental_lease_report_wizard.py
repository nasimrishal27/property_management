# -*- coding: utf-8 -*-
from odoo import fields, models


class RentalLeaseReportWizard(models.TransientModel):
    """ model for storing rental/lease details """
    _name = "rental.lease.report.wizard"
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
        where_clause = ["r.company_id = %s"]
        params = [self.env.company.id]
        if self.from_date:
            where_clause.append("date_start >= %s")
            params.append(self.from_date)
        if self.to_date:
            where_clause.append("date_end <= %s")
            params.append(self.to_date)
        if self.state:
            where_clause.append("r.state = %s")
            params.append(self.state)
        if self.tenant_ids:
            where_clause.append("tenant_id in %s")
            params.append(tuple(self.tenant_ids.ids))
        if self.owner_ids:
            where_clause.append("owner_id in %s")
            params.append(tuple(self.owner_ids.ids))
        if self.property_type:
            where_clause.append("property_type = %s")
            params.append(self.property_type)
        if self.property_ids:
            where_clause.append("property_id in %s")
            params.append(tuple(self.property_ids.ids))
        if where_clause:
            query += " WHERE " + " AND ".join(where_clause)
        self.env.cr.execute(query, params)
        report = self.env.cr.dictfetchall()
        data = {'report': report}
        return (self.env.ref('property_management.action_rental_lease_request_report')
                .report_action(None, data=data))
