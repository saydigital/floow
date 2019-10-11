# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
import time
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ProcessObject(models.Model):
    _name = 'syd_bpm.process_object'
    _description = 'Business Process Manager Object'
    
    name = fields.Char(string='Name',required=True)
    type=fields.Selection([
                          ('boolean', 'Boolean'),
                          ('char', 'Char'),
                          ('date', 'Date'),
                          ('datetime', 'Datetime'),
                          ('float', 'Float'),
                          ('html', 'Html'),
                          ('integer', 'Integer'),
                          ('many2one', 'Many2one'),
                          ('selection', 'Selection'),
                          ('text', 'Text')],string='Type')
    model_id = fields.Many2one('ir.model',string='Model')
    model = fields.Char('Model name',related="model_id.model")
    process_id = fields.Many2one('syd_bpm.process',string='Process',required=True)
    choices = fields.Char('Choices',placeholder="[('blue','Blue'),('yellow','Yellow')]",default=False)
    date_calculated = fields.Many2one('syd_bpm.process_date_calculated',string='Date Calculated From Start Process')
    attachment_type = fields.Selection([('process','Process'),('activity','Activity')], string="Attachment type")
    activity_ids = fields.Many2many('syd_bpm.activity', relation='syd_bpm_activity_process_object', column1='process_object_id', column2='activity_id', string='Attachment activities', domain="[('process_id','=',process_id)]")
    is_attachment = fields.Boolean(string="Is attachment")
    default_attachment = fields.Many2one('ir.attachment',string="Default attachment",domain=[('id','=','-1')])
    
    @api.multi
    @api.onchange('is_attachment')
    @api.constrains('is_attachment')
    def _set_model_id(self):
        for processObject in self:
            if processObject.is_attachment:
                processObject.type = 'many2one'
                processObject.model_id  = self.sudo().env['ir.model'].search([('model','=','ir.attachment')], limit=1).id
                
class CaseObject(models.Model):
    _name = 'syd_bpm.case_object'
    _description = 'Business Process Manager Object'

    
    name = fields.Char(related="process_object_id.name")
    process_object_id = fields.Many2one('syd_bpm.process_object',string='Process Object')
    case_id = fields.Many2one('syd_bpm.case',string='Case')
    process_id = fields.Many2one('syd_bpm.process',string='Process',related="process_object_id.process_id")
    val_boolean = fields.Boolean('Val Bool',default=False)
    val_char = fields.Char('Val Char',default=False)
    val_date = fields.Date('Val Date',default=False)
    val_datetime = fields.Date('Val Datetime',default=False)
    val_float = fields.Float('Val Float',default=False)
    val_html = fields.Html('Val Html',default=False)
    val_integer = fields.Integer('Val Int',default=False)
    val_selection = fields.Char('Val Selection',default=False)
    val_text = fields.Text('Val Text',default=False)
    parent_id = fields.Many2one('syd_bpm.case_object',string='Case Object with same name of Parent Case')
    
    res_id = fields.Integer('Res Id',default=False)
    
    
    @api.model
    def create(self, values):
        caseo =  super(CaseObject, self).create(values)
        
        ## set parent case object the object of the parent case with the same name
        for co in caseo.case_id.parent_id.case_object_ids:
            if (co.name == caseo.name):
                caseo.parent_id = co.id
        if caseo.process_object_id.type in ['date','datetime'] and bool(caseo.process_object_id.date_calculated):
            caseo.set_val(caseo.process_object_id.date_calculated.compute())
        return caseo
    
    @api.multi
    def get_val(self):
        """ 
             Get the val of the case object
        """
        self.ensure_one()
        if bool(self.parent_id):
            return self.parent_id.get_val()
        if self.process_object_id.type == 'many2one':
            if self.res_id == 0:
                return False
            return self.res_id
        else :
            return getattr(self,'val_%s'%(self.process_object_id.type))
        
    @api.multi
    def set_val(self,val):
        """ 
            Store the value of the case object
        """
        self.ensure_one()
        if bool(self.parent_id):
            return self.parent_id.set_val(val)
        if self.process_object_id.type == 'many2one':
            if bool(val):
                self.res_id = val.id
            else:
                self.res_id = False
        else :
            setattr(self,'val_%s'%(self.process_object_id.type),val)
    
    def is_attachment_loaded(self):
        if self.process_object_id.is_attachment and not self.process_object_id.default_attachment:
            attachment = self.sudo().env[self.process_object_id.model].browse(self.res_id)
            if attachment.type == 'url':
                return bool(attachment.url)
            else:
                return bool(attachment.checksum)
        return True
