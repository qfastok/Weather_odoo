# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

import logging
import csv
import io
import base64
from datetime import datetime


class FillWeather(models.TransientModel):
    _name = "weather.fill.wizard.line"
    _description = 'Fill description'

    weather_fill_wizard_id = fields.Many2one(
        'weather.fill.wizard', readonly=True)
    city = fields.Char(string='City', readonly=True)
    temperature_c = fields.Char(string='Temperature C', readonly=True)
    humidity = fields.Char(string='Humidity', readonly=True)
    error_description = fields.Char(readonly=True, size=150,
                                    string='Error Description')
    can_load = fields.Boolean(default=True)
    date = fields.Char(string='Date', readonly=True)


class FillWeatherLine(models.TransientModel):
    _name = "weather.fill.wizard"
    _description = 'Fill wizard'

    weather_file = fields.Binary(string='File', required=True)

    weather_filename = fields.Char(
        string='Filename')
    weather_fill_wizard_line_ids = fields.One2many(
        'weather.fill.wizard.line', 'weather_fill_wizard_id')
    file_parsed = fields.Boolean(default=False)
    data_uploaded = fields.Boolean(default=False)

    def parse_weather_fill_file(self):
        self.ensure_one()
        wizard_line = self.env['weather.fill.wizard.line'].sudo()
        view = self.env.ref('weather.filling_form')
        try:
            reader = csv.DictReader(
                io.StringIO(base64.b64decode(self.weather_file).decode("utf-8")))
        except Exception as e:
            logging.warning(e)
            raise UserError(
                _("Error when opening file. Please call administrator."))
        if not self.weather_filename.endswith('.csv'):
            raise UserError(
                _(f"Unable to load {self.weather_filename} file must be .csv"))
        columns = {'city', 'date', 'humidity', 'temperature_c'}
        for row in reader:
            error_description = ''
            can_load = True
            date_format = '%Y-%m-%d'

            if len(row.keys()) != len(columns) or set(row.keys()) != columns:
                raise UserError(
                    _("You have mistake in columns names!"))
            try:
                datetime.strptime(row['date'], date_format)
            except ValueError:
                error_description += 'Incorrect date format. '
                can_load = False

            try:
                float(row['humidity'])
                if not 100 > float(row['humidity']) >= 0:
                    error_description += "Humidity can't be more than 100%, " \
                                         "or lower than 0%"
                    can_load = False

            except ValueError:
                error_description += 'Humidity should be float. '
                can_load = False

            try:
                float(row['temperature_c'])
                if not 100 > float(row['temperature_c']) > -100:
                    error_description += "Temperature can't be higher than " \
                                         "100 or lower than -100!. "
                    can_load = False
            except ValueError:
                error_description += 'Temperature should be float. '
                can_load = False

            wizard_line.create({
                'weather_fill_wizard_id': self.id,
                'can_load': can_load,
                'error_description': error_description,
                'city': row['city'],
                'humidity': row['humidity'],
                'temperature_c': row['temperature_c'],
                'date': row['date'],
            })

        self.file_parsed = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'weather.fill.wizard',
            'view_id': view.id,
            'target': 'new',
        }

    def upload_weather(self):
        self.ensure_one()
        wizard_line_fill = self.env['city.weather'].sudo()
        ResCity = self.env['res.city'].sudo()
        country_ua = self.env.ref('base.ua')

        for line in self.weather_fill_wizard_line_ids:
            if not line.can_load:
                continue
            if wizard_line_fill.search([('city_id.name', '=', line.city),
                                        ('date', '=', line.date)]):
                line.can_load = False
                line.error_description = 'Date and City must be unique'
                continue

            city_id = ResCity.search([('name', '=', line.city)])
            if not city_id:
                city_id = ResCity.create(
                    {'name': line.city,
                     'country_id': country_ua.id})

            wizard_line_fill.create({
                'city_id': city_id.id,
                'humidity': float(line.humidity),
                'temperature_c': float(line.temperature_c),
                'date': line.date,
            })

        self.weather_fill_wizard_line_ids.filtered(
            lambda r: r.can_load).unlink()

        self.data_uploaded = True
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'weather.fill.wizard',
            'target': 'new',
        }

    def refresh_city_weather(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
