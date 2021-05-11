# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

import csv
import io
import base64
import datetime


class FillWeatherLine(models.TransientModel):
    _name = "weather.fill.wizard"
    _description = 'Fill wizard'

    weather_file = fields.Binary(string='File', required=True)

    weather_filename = fields.Char(
        string='Filename')
    weather_fill_wizard_line_ids = fields.One2many(
        'weather.fill.wizard.line', 'weather_fill_wizard_id')
    file_parsed = fields.Boolean(default=False)

    def parse_weather_fill_file(self):
        self.ensure_one()
        wizard_line = self.env['weather.fill.wizard.line'].sudo()
        view = self.env.ref('weather.filling_form')
        reader = csv.DictReader(
            io.StringIO(base64.b64decode(self.weather_file).decode("utf-8")))
        for row in reader:
            format = "%Y-%m-%d"
            error_description = ''
            can_load = True
            humidity = ''
            temperature_c = ''
            try:
                datetime.datetime.strptime(row['date'], format)
            except ValueError:
                error_description += 'Incorrect date format. '
                can_load = False
            try:
                humidity = float(row['humidity'])
            except ValueError:
                error_description += 'Humidity should be float. '
                can_load = False
            try:
                temperature_c = float(row['temperature_c'])
            except ValueError:
                error_description += 'Humidity should be float. '
                can_load = False
            if can_load:
                wizard_line.create({
                    'weather_fill_wizard_id': self.id,
                    'city': row['city'],
                    'humidity': humidity,
                    'temperature_c': temperature_c,
                    'date': fields.Date.to_date(row['date']),
                })
            else:
                wizard_line.create({
                    'weather_fill_wizard_id': self.id,
                    'error_description': error_description,
                })
                raise UserError(
                    _('You have incorrect data, check Error Description! '
                      'Error Description: ' + error_description))


        self.file_parsed = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'weather.fill.wizard',
            'view_id': view.id,
            'target': 'new',
        }

    # Method upload_weather: will get weather_fill_wizard_line_ids and creates
    # records to city.weather based on line data.
    # self.weather_fill_wizard_line_ids()  # method create

    def upload_weather(self):
        self.ensure_one()
        wizard_line_fill = self.env['city.weather'].sudo()
        ResCity = self.env['res.city'].sudo()
        country_ua = self.env.ref('base.ua')
        for line in self.weather_fill_wizard_line_ids:
            city_id = ResCity.search([('name', '=', line.city)])
            if not city_id:
                city_id = ResCity.create(
                    {'name': line.city,
                     'country_id': country_ua.id})
                # self.env.ref- посилання по xml.id
            wizard_line_fill.create({
                'city_id': city_id.id,
                'humidity': line.humidity,
                'temperature_c': line.temperature_c,
                'date': line.date,  # yyyy-mm-dd
            })


class FillWeather(models.TransientModel):
    _name = "weather.fill.wizard.line"
    _description = 'Fill description'

    weather_fill_wizard_id = fields.Many2one(
        'weather.fill.wizard', readonly=True)
    city = fields.Char(string='City', readonly=True)
    temperature_c = fields.Float(string='Temperature C', readonly=True)
    humidity = fields.Float(string='Humidity', readonly=True)
    error_description = fields.Char(readonly=True, size=150,
                                    string='Error Description')
    can_load = fields.Boolean(default=True)
    date = fields.Date(string='Date', readonly=True)
