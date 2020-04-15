# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
import time
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class DynamicFormLine(models.Model):
    _name = 'syd_bpm.dynamic_form_line'
    _order = 'sequence'
    _description ="Dynamic Form Line"
    
    
    def _get_name(self):
        for a in self:
            a.name = a.process_object_id.name
    
    string_field = fields.Char('String')            
    dynamic_form_id = fields.Many2one('syd_bpm.dynamic_form',required=True,ondelete='cascade')
    sequence = fields.Integer('Sequence')
    process_object_id = fields.Many2one('syd_bpm.process_object',required=True)
    required = fields.Boolean('Required')
    process_id = fields.Many2one('syd_bpm.process',string='Process', related="dynamic_form_id.process_id")
    name=fields.Char(compute='_get_name')
    
    
    @api.onchange('process_object_id')
    def _cancel_progress(self):
        for ele in self:
            ele.string_field = ele.name
    
                
class DynamicForm(models.Model):
    _name = 'syd_bpm.dynamic_form'
    _description='Dynamic Form'
    
    
    name = fields.Char('Name',required=True)
    note = fields.Text('Note',required=True)
    process_id = fields.Many2one('syd_bpm.process',string='Process', required=True)
    activity_ids = fields.One2many('syd_bpm.activity','dynamic_form_id')
    dynamic_form_line_ids = fields.One2many('syd_bpm.dynamic_form_line','dynamic_form_id')
    dynamic_wizard_id = fields.Many2one('syd_dynamic_wizard.wizard.config')
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft',string='State')
    
    
    def create_dynamic_wizard(self):
        """ 
            Create the dynamic wizard
        """
        for ele in self:
            vals = {'name':ele.name,
                    'note':ele.note,
                    'description':''
                    }
            _logger.info('creating dyn wizard with this data: {}'.format(vals))
            idwwc = self.env['syd_dynamic_wizard.wizard.config'].create(vals)
            for line in ele.dynamic_form_line_ids:
                vals = {'name':line.string_field,
                        'type_field':line.process_object_id.type,
                        'help':'',
                        'wizard_config_id':idwwc.id,
                        'required':line.required,
                        'choices':line.process_object_id.choices,
                        'model_id':line.process_object_id.model_id.id,
                        'domain':'[]',
                        'options' : ''
                        }
                
                if line.process_object_id.is_attachment:
                    vals['domain'] = "[('id','=','-1')]"
                    vals['options'] = "{'no_quick_create': True, 'no_create_edit' : True}"
                _logger.info('creating dyn wizard: {}'.format(vals))
                self.env['syd_dynamic_wizard.wizard.config.line'].create(vals)
            
            idwwc.model_create()
            ele.dynamic_wizard_id = idwwc.id
            
    @api.model
    def create(self, vals):
        ibdf = super(DynamicForm, self).create(vals)
        
        _logger.info('creating dyn form with id = {}'.format(ibdf.id))
        return ibdf
    
    
    def open_form(self,object,callback,values=False):
        """ 
            Shows the dynamic form
        """
        self.ensure_one()
        if (self.state != 'done'):
            raise ValidationError(_('Dynamic form not done!'))
        return self.dynamic_wizard_id.start_model_created(object,callback,defaults=values)
    
    
    def get_values_of_case(self,case_id):
        self.ensure_one()
        res = []
        for line in self.dynamic_form_line_ids:
                for co in case_id.case_object_ids:
                    if (line.process_object_id.id == co.process_object_id.id):
                        res.append({'name':line.process_object_id.name,'value':co.get_val()})
        return res
    
    
    def unlink(self):
        for a in self:
            self.env['syd_dynamic_wizard.wizard.config'].sudo().browse(a.dynamic_wizard_id.id).unlink()
        return super(DynamicForm,self).unlink()
    
    
    def set_done(self):
        """ 
            Create the Dynamic Wizard and link with the form
        """
        for a in self:
            a.sudo().create_dynamic_wizard()
            self.state = 'done'
    
    
    def write(self, vals):
        """ 
            Each time you modify the dynamic form, delete the dynamic wizard so you can set done again
        """
        ibdf = super(DynamicForm, self).write(vals)
        if (not 'dynamic_wizard_id' in vals and bool(self.dynamic_wizard_id) and not 'state' in vals):
            self.sudo().dynamic_wizard_id.unlink()
            self.state = 'draft'   
        return ibdf