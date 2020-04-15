# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
import time

class ProcessStart(models.TransientModel):
    _inherit = 'syd_bpm.process_start'
    
    parent_del_index = fields.Integer('Parent Del Index')
    
    
    def _val_case(self,case,process):
        res = super(ProcessStart,self)._val_case(case,process)
       
        res['pm_case_id'] = case['app_uid']
#         res['parent_del_index'] = self.parent_del_index
        return res
    
           
    def _val_task_executed(self,task,case_id):
        res = super(ProcessStart,self)._val_task_executed(task,case_id)
        activity_id = self.env['syd_bpm.activity'].search([('pm_activity_id','=',task['tas_uid'])])
        res['name'] = task['tas_title']
        res['pm_task_id']=task['tas_uid']
        res['pm_del_index']=task['del_index']  
        res['activity_id'] = activity_id.id
        return res
    
    
            
        
    