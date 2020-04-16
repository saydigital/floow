# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools import html2plaintext

class Note(models.Model):
    _inherit = ['note.note']
    
    
    process_id = fields.Many2one('syd_bpm.process',string='Process',related='case_id.process_id',ondelete='SET NULL')
    case_id = fields.Many2one('syd_bpm.case',string='Case')
    case_object_ids = fields.One2many('syd_bpm.case_object',related='case_id.case_object_ids')
    process_description = fields.Char('Process Description',related='case_id.description')
    task_executed_ids = fields.One2many('syd_bpm.task_executed','note_id',string='Task Executed')
    css_text_color = fields.Char('CSS Text color',related="process_id.css_text_color")
    css_background_color = fields.Char('CSS background color',related="process_id.css_background_color")
    dynamic_form_id = fields.Many2one('syd_bpm.dynamic_form',string="Dynamic Form",compute='_dynamic_form')
    form_compiled = fields.Boolean('Form Compiled',default=False)
    date_deadline = fields.Date(related='case_id.date_deadline')
    attachment_ids = fields.Many2many('ir.attachment', compute="_attachment_ids", string="Attachments")

    def _process_object(self,process_object_id,val):
        case_object_id = self.env['syd_bpm.case_object'].search([('process_object_id','=',process_object_id.id),('case_id','=',self.case_id.id)])
        for co in self.case_object_ids:
            if co.process_object_id.id == process_object_id.id:
                case_object_id = co
        case_object_id.set_val(val)
         
    
    def _dynamic_form(self):
        for n in self:
            dynamic_form_id = False
            for t in n.sudo().task_executed_ids:
                for a in t.activity_id:
                    dynamic_form_id = a.sudo().dynamic_form_id.id
            n.dynamic_form_id = dynamic_form_id
            
    
    def form_save(self,form):
        """ 
               Save the dynamic form
        """
        for f in self.dynamic_form_id.dynamic_form_line_ids:
            val = getattr(form,'x_%s' % f.name.lower().replace(' ','_')) 
            self._process_object(f.process_object_id,val)
        for line in self.dynamic_form_id.dynamic_form_line_ids:
            for co in self.case_object_ids:
                if line.process_object_id.id == co.process_object_id.id and not co.is_attachment_loaded():
                    self.form_compiled = False
                    return True
        self.form_compiled = True
        return True
    
    
    def open_form(self,object,callback):
        """ 
               Open the dynamic form
        """
        self.ensure_one()
        res = self.sudo().dynamic_form_id.get_values_of_case(self.case_id)
        return self.sudo().dynamic_form_id.open_form(object,callback,res)
    
    
    def action_close(self): 
        """ 
               Control if there is a dyn form and open it
        """
        for a in self:
            if not a.form_compiled and bool(a.dynamic_form_id):
                        return a.open_form(a,'form_save')
                    
        return super(Note, self).action_close()
          
    
    def write(self, values):
        """ 
               Note related to a process cannot be restored, in case you have to archive it it launch the next step
        """
        if (self.case_id) :
            if ('active' in values ):
                if (not values['active']) :
                    self.case_id.sudo().process_group_id._route_case_from_task(self.sudo().task_executed_ids)
                elif (values['active']) :
                    raise ValidationError('Process note cannot be restored')
            
        
        return super(Note, self).write(values)
    
    
    def next_process_step(self):
        """ 
            Next Proces step is computed when you archive a note
        """
        self.active=False
        return {'type': 'ir.actions.client', 'tag': 'history_back'}
        
    
    def _attachment_ids(self):
        for note in self:
            attachment_ids = []
            
            for case_object in note.case_object_ids:
                if case_object.process_object_id.is_attachment:
                    if case_object.process_object_id.attachment_type == 'process':
                        if case_object.res_id:
                            if case_object.is_attachment_loaded():
                                attachment_ids.append(case_object.res_id)
                        if case_object.process_object_id.default_attachment:
                            attachment_ids.append(case_object.process_object_id.default_attachment.id)
                            
                    elif case_object.process_object_id.attachment_type == 'activity':
                        for task_executed in note.task_executed_ids:
                            if task_executed.activity_id in case_object.process_object_id.activity_ids:
                                if case_object.res_id:
                                    if case_object.is_attachment_loaded():
                                        attachment_ids.append(case_object.res_id)
                                if case_object.process_object_id.default_attachment:
                                    attachment_ids.append(case_object.process_object_id.default_attachment.id)
            note.attachment_ids = attachment_ids
