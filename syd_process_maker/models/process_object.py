# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
import time
from odoo.exceptions import ValidationError


class ProcessObject(models.Model):
    _inherit = 'syd_bpm.process_object'
    
    pm_type = fields.Char(string='ProcessMaker Type')
    pm_accepted_values=fields.Char('Accepted Values')
    pm_variable_id=fields.Char('Process Maker Id')

    def _get_odoo_type(self,pm_type,pm_accepted_values):
        if bool(pm_accepted_values):
            return 'selection'
        if (pm_type=='String'):
            return 'char'
        if pm_type == 'Integer':
            return 'integer'
        if pm_type == 'Float':
            return 'float'
        if pm_type == 'Boolean' :
            return 'boolean'
        if pm_type == 'Datetime':
            return 'datetime'
        else:
            return pm_type
        
       
    def _get_choices(self,accepted_values):
        res = "["
        if bool(accepted_values):
            list_choices = eval(accepted_values)
            for c in list_choices:
                res += "('%s','%s')," % (c['value'],c['label'])
            res +="]"
            return res
        else :
            return False
    
    @api.model
    def create(self, vals):
        accepted_values = vals['pm_accepted_values'] if 'pm_accepted_values' in vals else False
        if ('pm_type' in vals and 'type' not in vals):
            vals['type'] = self._get_odoo_type(vals['pm_type'],accepted_values)
        if (accepted_values and 'choices' not in vals) :
            vals['choices'] = self._get_choices(accepted_values)
        return super(ProcessObject, self).create(vals)

    
    
    def write(self, vals):
        accepted_values = vals['pm_accepted_values'] if 'pm_accepted_values' in vals else self.pm_accepted_values
        if ('pm_type' in vals and 'type' not in vals):
            vals['type'] = self._get_odoo_type(vals['pm_type'],accepted_values)
        if (accepted_values and 'choices' not in vals) :
            vals['choices'] = self._get_choices(accepted_values)
        return super(ProcessObject, self).write(vals)
        