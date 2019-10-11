# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
import odoo
from odoo.exceptions import ValidationError


class OdooConfiguration(models.TransientModel):
   
    _inherit = 'res.config.settings'
    
    
    activity_type_id = fields.Many2one(
        'mail.activity.type', 'Activity Type',config_parameter='syd_bpm.activity_type_id')
    module_syd_bpm_activity = fields.Boolean(string='Activity on note')
    
    module_syd_process_maker = fields.Boolean(string='Process Maker Integration')
    
    
