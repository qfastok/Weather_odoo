# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class FillWeatherLine(models.TransientModel):
    _name = "fill.weather.line"
    _description = 'Fill desctiption'

    filling_date = fields.Char(string='Date')
    filling_city = fields.Char(string='City')
    filling_humidity = fields.Char(string='Humidity')
    filling_temperature_c = fields.Char(string='Temp c')




class FillWeather(models.TransientModel):
    _name = "fill.weather"
    _description = 'Fill desctiption'

    wizard_file = fields.Binary()
    wizard_file_name = fields.Char()
    # wizard_fill_line_ids = fields.One2many()
