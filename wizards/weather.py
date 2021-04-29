# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AutoFill(models.TransientModel):
    _name = "fill.demo"
    _description = 'Fill desctiption'

    fill_demo = fields.Char(string='Check')
    filling_customer = fields.Char(string='Customer')
    filling_saleperson = fields.Char(string='Saleperson')
