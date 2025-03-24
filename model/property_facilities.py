# -*- coding: utf-8 -*-
from odoo import fields, models


class PropertyFacilities(models.Model):
    """ Facilities """
    _name = "property.facilities"
    _description = "Property Facilities"

    name = fields.Char('Facilities', required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', "Facility is already exists!")]
