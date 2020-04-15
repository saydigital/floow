# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo
from odoo import api, fields, models, tools
import urllib.request
import requests
import time
class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'
    
    state= fields.Selection(selection_add=[("process", "Launch BPM Process"),("activity", "Complete BPM Activity")])
    process_id = fields.Many2one('syd_bpm.process', string='Process')
    user_id = fields.Many2one('res.users', string='User')
    activity_id = fields.Many2one('syd_bpm.activity', string='BPM Activity')
    
    def _get_process_start_record(self,record=False):
        """ 
            Get the name of the case from the automatic action
        """
        today_in_millis = int(round(time.time() * 1000))
        
        return {
            'name' : self.process_id.name + '-'+(record.display_name if record else str(today_in_millis)),
            'user_id' : self.user_id.id
        }
    
    def _close_tasks(self,record=False):
        """ 
            Close Task if the record is a process object of the case related to this task
        """
        task_ids = self.sudo().env['syd_bpm.task_executed'].search([
            ('process_id','=',self.process_id.id),
            ('activity_id','=',self.activity_id.id),
            ('is_task_active','=', True)
        ])
        if not record:
            return
        case_id = False
        for task_id in task_ids:
            case_id = task_id.case_id
            for co in task_id.case_id.case_object_ids:
                if (
                    co.process_object_id.model and 
                    co.process_object_id.model == record._name and 
                    co.res_id == record.id
                ):
                    if task_id.note_id.dynamic_form_id:
                        if task_id.note_id.form_compiled:
                            if task_id.note_id.action_close():
                                task_id.note_id.next_process_step()
                                
                    elif task_id.note_id.action_close():
                        task_id.note_id.next_process_step()
        return case_id
        
                        
                        
    @api.model
    def run_action_process_multi(self, action, eval_context=None):
            """ 
                Run a process automatic action
            """
            eval_context = self._get_eval_context(action)
            record = eval_context.get('record',False)
            process_start = self.sudo().env['syd_bpm.process_start'].create(
                                action._get_process_start_record(record)
                            )    
            case_id = process_start.trigger_process(
                                action.process_id, record 
                            )
            eval_context = action.with_context({'case':case_id})._get_eval_context(action)
            eval_context['record']=record
            self.with_context(eval_context['env'].context).run_action_code_multi(action,eval_context)
            if 'action' in eval_context:
                return eval_context['action']

    
    def run_action_activity_multi(self, action, eval_context=None):
            """ 
                Close a task automatic action
            """
            eval_context = action._get_eval_context(action)
            record = eval_context.get('record',False)
            case_id = action._close_tasks(record)
            eval_context = action.with_context({'case':case_id})._get_eval_context(action)
            eval_context['record']=record
            action.with_context(eval_context['env'].context).run_action_code_multi(action,eval_context)
            if 'action' in eval_context:
                return eval_context['action']
            
    @api.model
    def _get_eval_context(self, action=None):
        """ 
               Create the eval context with the process object 
        """
        eval_context = super(IrActionsServer,self)._get_eval_context(action)
        context = self._context
        if ('case' in context):
            case = context['case']
            for co in case.case_object_ids:
                value = co.get_val()
                if (
                    co.process_object_id.type == 'many2one' and 
                    value != 0
                ):
                    eval_context[co.name] = self.env[co.process_object_id.model].browse(value)
                else :
                    eval_context[co.name] = value
        eval_context['urllib2']=urllib.request
        eval_context['requests']=requests
        return eval_context
    
    @api.model
    def run_action_code_multi(self, action, eval_context=None):
        """ 
               Run the code and update the process objects
        """
        action = super(IrActionsServer,self).run_action_code_multi(action,eval_context)
        context = self._context
        if ('case' in context):
            case = context['case']
            for co in case.case_object_ids:
                if co.name in eval_context:
                    if co.process_object_id.type == 'many2one':
                        co.set_val(self.env[co.process_object_id.model].browse(eval_context[co.name]))
                    else:
                        co.set_val(eval_context[co.name])
        return action