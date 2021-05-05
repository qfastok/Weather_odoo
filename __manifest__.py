# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Weather',
    'version': '1.0',
    'category': 'Weather.Weather',
    'description': """
Demo lesson for N-Dev.
""",
    'depends': [
        'base',
        'uom',
    ],
    'data': [
        'security/weather_security.xml',
        'security/ir.model.access.csv',
        'wizards/weather_fill.xml',
        'views/weather.xml',
        'data/weather_decimal_precision.xml',
        'data/uom_uom.xml',
    ],
    'demo': [],
    'installable': True,
    'license': 'AGPL-3',
}
