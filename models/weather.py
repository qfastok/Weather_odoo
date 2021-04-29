# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError


class Weather(models.Model):
    _name = "city.weather"
    _description = "Weather model"

    name = fields.Char(string='name')
    city_id = fields.Many2one('res.city', string='City', required=True, index=True, readonly=True,
                              states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft')  # states={'draft': [('readonly', False)]})

    date = fields.Date(string='Date', required=True, index=True, readonly=True, states={'draft': [('readonly', False)]})
    humidity = fields.Float(string='Humidity %', default=0.1, readonly=True, states={'draft': [('readonly', False)]})  # rounding
    temperature_c = fields.Float(string='Celsius', readonly=True, store=True,
                                 states={'draft': [('readonly', False)]})  # rounding
    temperature_uom_c_id = fields.Many2one('uom.uom', readonly=True)  # default C(celsius degrees) required=True
    temperature_f = fields.Float(string='Fahrenheit', compute='_compute_fahrenheit_temperature',
                                 readonly=True, store=True, )  # rounding
    temperature_uom_f_id = fields.Many2one('uom.uom', readonly=True, required=True)  # default F(Fahrenheits)

    _sql_constraints = [
        ('temperature_check', 'CHECK(temperature_c > -100 AND temperature_c < 100)',
         "Temperature can't be higher than 100 or lower than -100!"),
        ('unique_check', 'unique (date,city_id)', 'Date and City must be unique'),
        ('humidity_check', 'CHECK(humidity < 100 AND humidity > 0)',
         "Humidity can't be more than 100%, or lower than 0%"),
    ]

    @api.depends('temperature_c', 'temperature_f')
    def _compute_fahrenheit_temperature(self):
        for r in self:
            if not r.temperature_c:
                r.temperature_f = 32.0
            else:
                r.temperature_f = 32 + 1.8 * r.temperature_c

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    @api.constrains('date')
    def _check_date(self):
        for check in self:
            if check.date > fields.Date.today():
                raise ValidationError(_("Date can't be higher than today."))

    # _sql_constraints = [
    #     ('adyen_uuid_uniq', 'UNIQUE(adyen_uuid)', 'Adyen UUID should be unique'),
    # ]
