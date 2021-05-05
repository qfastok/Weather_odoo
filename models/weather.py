# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from odoo.modules.module import get_module_resource

import base64


class Weather(models.Model):
    _name = "city.weather"
    _description = "Weather model"

    @api.model
    def _default_temperature_celsius(self):
        return self.env.ref('weather.temperature_uom_celsius')

    @api.model
    def _default_temperature_fahrenheit(self):
        return self.env.ref('weather.temperature_uom_fahrenheit')

    city_id = fields.Many2one(
        'res.city', string='City', required=True,
        index=True, readonly=True,
        states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string='Status',
        default='draft', states={'draft': [
            ('readonly', False)]})

    date = fields.Date(
        string='Date', required=True, index=True, readonly=True,
        states={'draft': [('readonly', False)]})

    humidity = fields.Float(
        string='Humidity %', default=0.1, readonly=True,
        digits=dp.get_precision('weather_rounding'),
        states={'draft': [('readonly', False)]})

    temperature_c = fields.Float(
        string='Celsius', readonly=True, store=True,
        digits=dp.get_precision('weather_rounding'),
        states={'draft': [('readonly',
                           False)]})

    temperature_uom_c_id = fields.Many2one(
        'uom.uom', readonly=True,
        default=_default_temperature_celsius)

    temperature_f = fields.Float(
        string='Fahrenheit',
        compute='_compute_fahrenheit_temperature',
        digits=dp.get_precision('weather_rounding'),
        readonly=True, store=True,
    )

    temperature_uom_f_id = fields.Many2one(
        'uom.uom', readonly=True,
        default=_default_temperature_fahrenheit)

    _sql_constraints = [
        ('temperature_check',
         'CHECK(temperature_c > -100 AND temperature_c < 100)',
         "Temperature can't be higher than 100 or lower than -100!"),
        ('unique_check', 'unique (date,city_id)',
         'Date and City must be unique'),
        ('humidity_check', 'CHECK(humidity < 100 AND humidity > 0)',
         "Humidity can't be more than 100%, or lower than 0%"),
    ]

    @api.depends('temperature_c')
    def _compute_fahrenheit_temperature(self):
        for r in self:
            r.temperature_f = 32 + 1.8 * r.temperature_c

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    @api.constrains('date')
    def _check_date(self):
        for check in self:
            if check.date > fields.Date.today():
                raise ValidationError(_("Date can't be higher than today."))

    def create_invoice_from_file(self, module_name, subfolder, filename):
        file_path = get_module_resource(module_name, 'test_file', filename)
        file = open(file_path, 'rb').read()

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.encodebytes(file),
            'res_model': 'account.move',
        })
