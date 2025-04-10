# -*- coding: utf-8 -*-
import base64

from odoo import fields, models
from odoo.exceptions import ValidationError
import io
import json
import xlsxwriter
from odoo import models
from odoo.tools import json_default


ORDER_STATE = [
    ("draft", "Draft"), ("to-approve", "To Approve"), ("confirm", "Confirmed"),
    ("close", "Closed"), ("return", "Returned"), ("expired", "Expired")
]
TYPE = [("rent", "Rent"), ("lease", "Lease")]

class RentalLeaseReportWizard(models.TransientModel):
    """ model for storing rental/lease details """
    _name = "rental.lease.report.wizard"
    _description = "Rental/Lease Management PDF Report"

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    state = fields.Selection(selection=ORDER_STATE)
    tenant_ids = fields.Many2many(comodel_name="res.partner", string="Tenant")
    owner_ids = fields.Many2many(comodel_name='res.partner', string="Owner",
                                 relation="res_partner_rental_lease_report_wizard_owner_id_rel")
    property_type = fields.Selection(selection=TYPE, string="Type")
    property_ids = fields.Many2many(comodel_name='property.property', string="Property")

    def action_print_pdf(self):
        """Function for printing XLSX report"""
        data = self._prepare_report_data()
        return (self.env.ref('property_management.action_rental_lease_request_report')
                .report_action(None, data=data))

    def action_print_xlsx(self):
        """Function for printing XLSX report"""
        data = self._prepare_report_data()
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'rental.lease.report.wizard',
                     'options': json.dumps(data, default=json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Rental Lease Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center', 'bold': True})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        filter_txt = workbook.add_format({'font_size': '10px', 'align': 'left', 'bold': True})
        wrap_format = workbook.add_format({'text_wrap': True, 'font_size': '6px', 'align': 'center', 'bold': True})
        logo = self.env.company.logo
        company = self.env.company
        company_info = f"""{company.name}
        {company.street} {company.street2}
        {company.city}, {company.state_id.name} {company.zip}
        {company.country_id.name}"""
        if logo:
            image_stream = io.BytesIO(base64.b64decode(logo))
            image_stream.seek(0)
            sheet.insert_image('M2', 'logo.png', {
                'image_data': image_stream,
                'x_scale': 0.1,
                'y_scale': 0.08,
            })
        sheet.merge_range('B2:K3', 'RENTAL/LEASE REPORT', head)
        sheet.merge_range('L2:N6', ' ', wrap_format)
        sheet.write('L2', company_info, wrap_format)
        sheet.merge_range('A9:B9', 'Sequence', cell_format)
        sheet.merge_range('C9:D9', 'Property', cell_format)
        sheet.merge_range('E9:F9', 'Tenant', cell_format)
        sheet.merge_range('G9:H9', 'Owner', cell_format)
        sheet.merge_range('I9:J9', 'Amount', cell_format)
        sheet.merge_range('K9:L9', 'Type', cell_format)
        sheet.merge_range('M9:N9', 'State', cell_format)
        filters = []
        if data.get('from_date'):
            filters.append(f"From Date: {data.get('from_date')}")
        if data.get('to_date'):
            filters.append(f"To Date: {data.get('to_date')}")
        if data.get('state'):
            filters.append(f"State: {data.get('state')}")
        if data.get('type'):
            filters.append(f"Property Type: {data.get('type')}")
        if filters:
            filter_text = f"{' ' * 31}".join(filters)
            sheet.merge_range('A8:N8', filter_text, filter_txt)

        for i, report in enumerate(data.get('report'), start=10):
            sheet.merge_range(f'A{i}:B{i}', report.get('name'), txt)
            sheet.merge_range(f'C{i}:D{i}', report.get('property'), txt)
            sheet.merge_range(f'E{i}:F{i}', report.get('partner'), txt)
            sheet.merge_range(f'G{i}:H{i}', report.get('owner'), txt)
            sheet.merge_range(f'I{i}:J{i}', f"${report.get('price')}", txt)
            sheet.merge_range(f'K{i}:L{i}', report.get('property_type'), txt)
            sheet.merge_range(f'M{i}:N{i}', report.get('state'), txt)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def _prepare_report_data(self):
        """Function for printing report"""
        query = """SELECT r.name,p.name as partner,pr.name as property,l.price_subtotal as price,
                    r.property_type,r.state,pr.owner_id as owner
                    FROM rental_lease r join res_partner p on tenant_id = p.id
                    join rental_lease_order_line l on l.order_id = r.id
                    join property_property pr on l.property_id = pr.id"""
        where_clause = ["r.company_id = %s"]
        params = [self.env.company.id]
        if self.from_date:
            where_clause.append("date_start >= %s")
            params.append(self.from_date)
        if self.to_date:
            if self.from_date:
                if self.to_date < self.from_date:
                    raise ValidationError("You can only add a 'To Date' that is greater than 'From Date'")
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
        for rec in report:
            rec['owner'] = self.env['res.partner'].browse(rec.get('owner')).name
            rec['state'] = dict(ORDER_STATE).get(rec.get('state'))
            rec['property_type'] = dict(TYPE).get(rec.get('property_type'))
        data = {'from_date': self.from_date, 'to_date': self.to_date, 'state': dict(ORDER_STATE).get(self.state),
                'type': dict(TYPE).get(self.property_type), 'report': report}
        if report:
            return data
        else:
            raise ValidationError("This condition is not satisfactory in any record")