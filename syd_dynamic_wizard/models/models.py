# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
import datetime


import logging

_logger = logging.getLogger(__name__)

class WizardConfigLine(models.Model):
    _name = 'syd_dynamic_wizard.wizard.config.line'
    _description = "Wizard Config Line"
    name = fields.Char('Field Name')
    type_field = fields.Selection([('binary', 'Binary'),
                          ('boolean', 'Boolean'),
                          ('char', 'Char'),
                          ('date', 'Date'),
                          ('datetime', 'Datetime'),
                          ('float', 'Float'),
                          ('html', 'Html'),
                          ('integer', 'Integer'),
                          ('many2many', 'Many2many'),
                          ('many2one', 'Many2one'),
                          ('monetary', 'Monetary'),
                          ('one2many', 'One2many'),
                          ('reference', 'Reference'),
                          ('selection', 'Selection'),
                          ('text', 'Text')],default='char')
    help = fields.Char('Help')
    wizard_config_id = fields.Many2one('syd_dynamic_wizard.wizard.config',ondelete='cascade')
    model_id = fields.Many2one('ir.model',string='Relation Model')
    field_relation = fields.Char('Relation Field')
    choices = fields.Char('Possible Choices')
    required = fields.Boolean('Required')
    domain = fields.Char('Domain')
    options = fields.Char('Options')


    
    
        
class WizardConfig(models.Model):
    _name = 'syd_dynamic_wizard.wizard.config'
    _description=' Wizard Config'
    
    name = fields.Char('Name Wizard')
    note = fields.Text('Note',help='Note inside dynamic wizard form',required=True)
    description = fields.Char('Info')
    wizard_config_line_ids = fields.One2many('syd_dynamic_wizard.wizard.config.line','wizard_config_id',string='Field')
    model_id = fields.Many2one('ir.model')
    view_id = fields.Many2one('ir.ui.view')
    
    
    
    def unlink(self):
        for a in self:
            a.delete_model_created()
        return super(WizardConfig,self).unlink()
    
    def delete_model_created(self):
        _logger.info('Eliminating {} e il model {}'.format(self.view_id,self.model_id))
        self.env['ir.model.data'].search([('res_id','=',self.view_id.id)]).unlink()
        self.view_id.unlink()
        self.model_id.unlink()

    
    def start_model_created(self,object,callback,defaults=False):
        action = {
            'name':'',
            'res_model':self.model_id.model,
            'view_mode':'form',
            'target':'new',
            'type':'ir.actions.act_window',
            'context': {'model':object._name,'res_id':object.id,'callback':callback,'syd_dynamic_wizard':True}
            }
        if defaults:
            for d in defaults:
                if d['value']: 
                    action['context']['default_'+'x_%s' % d['name'].lower().replace(' ','_')]=d['value']
        return action
    
    
        
    def model_create(self):
        vals_model = {'model':'x_' + self.name.lower(),
                      'name':'syd_' + self.name,
                      'info':self.description,
                      'transient':True
                      }
        _logger.info('Sto creando un model con questi dati: {}'.format(vals_model))
        im = self.env['ir.model'].sudo().create(vals_model)
        self.model_id = im.id
        
         
        for ele in self.wizard_config_line_ids:
            vals_fields = {'model':im.model,
                           'model_id':im.id,
                           'name':'x_' + ele.name.lower().replace(' ','_'),
                           'state':'manual',
                           'field_description':ele.name,
                           'help':ele.help,
                           'ttype':ele.type_field,
                           'relation':ele.model_id.model,
                           'relation_field':ele.field_relation,
                           'required':ele.required,
                           'selectable':True,
                           'store':True,
                           'index':False,#gestire il caso
                           'related':False,#gestire il caso
                           'readonly':False,#gestire il caso
                           'translate':False,#gestire il caso
                           'column1':'',#gestire il caso
                           'column2':'',#gestire il caso
                           'domain': ele.domain,
                           'selection':ele.choices,
                           'on_delete':'',
                           'depends':False,#gestire il caso
                           'complete_name':False,#gestire il caso
                           'compute':False}#gestire il caso
            _logger.info('Sto creando il campo con questi dati: {}'.format(vals_fields))
            imf = self.env['ir.model.fields'].sudo().create(vals_fields)
            
         

       

        
        type_view = ['form']
        for ele in type_view:
            
            vals_model_data = {'noupdate':True,
                               'name':'view_menu_prova_' + self.name,
                               'date_init':datetime.datetime.now(),
                               'date_update':datetime.datetime.now(),
                               'module':'syd_dynamic_wizard',
                               'model':im.model}
            _logger.info('Creating ir.model.data with data: {}'.format(vals_model_data))
            imd = self.env['ir.model.data'].sudo().create(vals_model_data)
            
 
            view_text = '<?xml version="1.0"?><' + ele + ' string="' + self.name + '"><p>'+self.note+'</p><group>'
            for f in self.wizard_config_line_ids:
                view_text = view_text + '<field name="' + 'x_' + f.name.lower().replace(' ','_') + '"' + ((' options="' + f.options + '"') if bool(f.options) else '') + "/>"
            view_text = view_text + '</group>'
            view_text = view_text + '<footer><button type="object" string="Save" name="confirm_wizard" /></footer>'
            view_text = view_text + '</' + ele + '>'
            
            
            vals_view = {
                         'type':'form',
                         'arch':view_text,
                         'name':self.name + ele,
                         'model':im.model}
            _logger.info('Sto creando la vista view con questi dati: {}'.format(vals_view))
            iuv = self.env['ir.ui.view'].sudo().create(vals_view)
            self.view_id = iuv.id
            
             
            imd.write({'res_id':iuv.id})