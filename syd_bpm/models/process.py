# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import misc
from datetime import datetime
import time
from odoo.exceptions import ValidationError
import abc

class BPMInterface:
    __metaclass__ = abc.ABCMeta
    """ 
            Interface of the integration between odoo and BPM tool
    """
        
        
    @abc.abstractmethod
    def _call(self,request,jsonobject=dict(),method='GET'):
        """ 
            Call the WS and manage the authentication
        """
        pass
    
    @abc.abstractmethod
    def _get_process_list(self):
        """ 
            Retrieve the list of the processes
        """
        pass
    
    @abc.abstractmethod
    def _get_activity_list(self,process_id):
        """ 
            Retrieve the list of the activities
        """
        pass
    
    @abc.abstractmethod
    def _get_starting_activity(self):
        """ 
            Get the starting activity
        """
        # GET /case/start-cases
        pass
    
    @abc.abstractmethod
    def _route_case(self,case_id,del_index=False):
        """ 
            Let the case to go to the next step
        """
        pass
    
    @abc.abstractmethod
    def _get_current_tasks(self,case_id):
        """ 
            Retrieve the current tasks (after the route)
        """
        pass
    
    
    @abc.abstractmethod
    def _get_process_map(self,process_id):
        """ 
            Get the png in bpmn of the process
        """
        pass
      
      
    @abc.abstractmethod
    def _get_case_variables(self,case_id):
        """ 
            Get the case variables that you use for the gateway
        """
        #GET /cases/{app_uid}/variables
        pass         
     
    @abc.abstractmethod
    def _set_case_variables(self,case_id,data):
        """ 
            set the case variables that you use for the gateway
        """
        pass
        
    @abc.abstractmethod
    def _get_process_variables(self,process_id):
        #GET /api/1.0/{workspace}/project/{prj_uid}/process-variables
        """ 
            Get the process variables that you use for the gateway
        """
        pass
    
    @abc.abstractmethod
    def _get_case_info(self,case_id):
        """ 
            Get the general information of the case
        """
        pass
    
    @abc.abstractmethod
    def _get_activity_info(self,process_id,activity_id):
        """ 
            Get the general information of the activity
        """
        pass
    
    @abc.abstractmethod
    def _get_category_info(self,cat_id):
        """ 
            Get the general information of the process category
        """
        pass
    
    @abc.abstractmethod
    def _get_assign_user(self):
        """ 
            Get the user that you use on the BPM tool to assign all the task
        """
        pass
    
    @abc.abstractmethod
    def _get_user_of_task(self,process_id,task_id):
        """ 
            Get the user of this task
        """
        pass
    
    @abc.abstractmethod
    def _assign_user_to_task(self):
        """ 
            Assign the general user tho the task
        """
        pass
    
    @abc.abstractmethod
    def _set_variable(self,case):
        """ 
            Set a variable
        """
        pass
    
    @abc.abstractmethod
    def _start_process(self,process_id,activity_id):
        """ 
            Start a process
        """
        pass
    
    @abc.abstractmethod
    def _cancel_case(self,case_id):
        """ 
            Cancel a case
        """
        pass
    
    @abc.abstractmethod
    def update_processes(self):
        """ 
            Update the process on odoo based on bpm tool modification
        """
        pass
    
    @abc.abstractmethod
    def _route_case_from_task(self,task_executed_id):
        """ 
            Next case task from a specific task
        """
        pass
    
class ProcessGroup(models.Model):
    _name = 'syd_bpm.process_group'
    _description = 'Process Group'
    _inherit = ['mail.thread']
    
    name = fields.Char(string='Name',required=True)
    description = fields.Char(string='Description')
    last_update = fields.Datetime(string='Last Update')
    process_ids = fields.One2many('syd_bpm.process','process_group_id',string="Processes")    
    type=fields.Selection([],string='Type')
    

class ProcessCategory(models.Model):
    _name = 'syd_bpm.process_category'
    _description = 'Process Category'
    _inherit = 'mail.thread'
    
    name = fields.Char(string='Name',required=True)
    description = fields.Char(string='Description')
    process_ids = fields.One2many('syd_bpm.process','category_id',string="Processes")

    @api.model
    def get_or_create_category(self,category_name):
        if (not category_name):
            return False
        category_id = self.env['syd_bpm.process_category'].search([('name','=',category_name)],limit=1)
        if (not bool(category_id)):
            category_id = self.env['syd_bpm.process_category'].create({'name':category_name})
        return category_id.id
        
class ProcessPriority(models.Model):
    _name = 'syd_bpm.process_priority'
    _description = 'Process'
    
    name = fields.Char('Name')
    css_text_color = fields.Char('CSS Text color',default="grey")
    css_background_color = fields.Char('CSS background color',default="white")
             
class Process(models.Model):
    _name = 'syd_bpm.process'
    _description = 'Process'
    _inherit = 'mail.thread'
    
    name = fields.Char(string='Name',required=True)
    description = fields.Char(string='Description')
    process_group_id = fields.Many2one('syd_bpm.process_group','Process Group',required=True)
    activity_ids = fields.One2many('syd_bpm.activity','process_id',string="Activities")
    activity_ids_count =  fields.Integer('Number of activities',compute="get_activity_count")
    case_ids = fields.One2many('syd_bpm.case','process_id',string="Cases")
    process_object_ids = fields.One2many('syd_bpm.process_object','process_id',string="Process Objects")
    case_ids_count = fields.Integer('Number active case',compute="get_active_case")
    category_id = fields.Many2one('syd_bpm.process_category','Process Category',required=False)
    priority_id = fields.Many2one('syd_bpm.process_priority','Process Priority',required=False)
    map = fields.Html('Map')
    locked = fields.Boolean('Locked')
    startable = fields.Boolean('Startable')
    deprecated = fields.Boolean('Deprecated',default=False)
    css_text_color = fields.Char('CSS Text color',related="priority_id.css_text_color")
    css_background_color = fields.Char('CSS background color',related="priority_id.css_background_color")
    date_deadline = fields.Many2one('syd_bpm.process_object',domain="[('type','=','date')]")
    attachment_ids = fields.One2many('syd_bpm.process_object','process_id', string="Attachments", domain=[('attachment_type','!=',False)])
    
    dynamic_form_ids = fields.One2many('syd_bpm.dynamic_form','process_id',string='Dynamic form')
    process_role_ids = fields.Many2many('syd_bpm.process_role',string='Process Roles', compute='_compute_process_role_ids')
    

    @api.depends('activity_ids')
    def _compute_process_role_ids(self):
        for ele in self:
            ids = []
            for activity in ele.activity_ids:
                if activity.process_role_activity_id.id:
                    ids.append(activity.process_role_activity_id.id)
            ele.process_role_ids = ids
            
    
    def get_activity_count(self):
        for p in self:
            p.activity_ids_count = len(p.sudo().activity_ids)
            
    
    def get_active_case(self):
        for p in self:
            p.case_ids_count = self.sudo().env['syd_bpm.case'].search([('process_id','=',p.id),('state','=','in_progress')],count=True)      




   
           
class Activity(models.Model):
    _name = 'syd_bpm.activity'
    _description = 'Activity'
    _table = 'syd_bpm_activity'
    
    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Name',required=True)
    process_id = fields.Many2one('syd_bpm.process',string='Process',required=True,readonly=True,ondelete='cascade')
    user_id = fields.Many2one('res.users',string='User')
    description = fields.Char('Description')
    is_start_activity = fields.Boolean('Is Starting')
    type = fields.Selection([
                ('user-fixed', "Specific User"),
                ('user-case',"User of Process Case"),
                ('dynamic-user',"Dynamic User"),
                ('process-role',"Process Role"),
                ('automated', "Automated"),
                ('sub-process',"Sub Process"),
            ], default='user-case',track_visibility='onchange',required=True)
    action = fields.Many2one('ir.actions.server',string='Action')
    sub_process_id = fields.Many2one('syd_bpm.process',string='Sub Process')
    deprecated = fields.Boolean('Deprecated',default=False)
    date_deadline = fields.Many2one('syd_bpm.process_object',domain="[('type','=','date'),('process_id','=',process_id)]")
    dynamic_form_id = fields.Many2one('syd_bpm.dynamic_form',string="Dynamic Form",domain="[('state','=','done'),('process_id','=',process_id)]")
    dynamic_user_id = fields.Many2one('syd_bpm.process_object',string="Dynamic User" ,domain="[('type','=','many2one'),('model','=','res.users'),('process_id','=',process_id)]")
    process_role_activity_id = fields.Many2one('syd_bpm.process_role_activity',string="Process Role Activity")
    attachment_ids = fields.Many2many('syd_bpm.process_object', relation='syd_bpm_activity_process_object', column1='activity_id', column2='process_object_id', string='Attachments', domain="[('process_id','=',process_id),('attachment_type','!=', False)]")



class Case(models.Model):
    _name = 'syd_bpm.case'
    _description = 'Case'
    _table = 'syd_bpm_case'
    
    
    name = fields.Char(string='Name',required=True)
    process_name = fields.Char('Process name')
    process_id = fields.Many2one('syd_bpm.process',string='Process',ondelete='SET NULL')
    task_list = fields.Many2many('syd_bpm.task_executed')
    process_group_id = fields.Many2one('syd_bpm.process_group',related='process_id.process_group_id')
    task_executed_ids = fields.One2many('syd_bpm.task_executed','case_id',string="Task Executed")
    description = fields.Char('Case Description')
    state=fields.Selection([('completed','Completed'),('cancelled','Cancelled'),('in_progress','In Progress')],default='in_progress')
    case_object_ids = fields.One2many('syd_bpm.case_object','case_id',string="Case Objects")
    date_task_start = fields.Datetime('Date Start',compute="get_date_and_task")
    date_task_end = fields.Datetime('Date End',compute="get_date_and_task")
    task_active = fields.Char('Task active', compute="get_date_and_task")
    detail = fields.Html('Case Detail')
    parent_id = fields.Many2one('syd_bpm.case',string='Parent Case',related="parent_task_id.case_id")
    user_id = fields.Many2one('res.users',string='User of Process Case')
    date_deadline = fields.Date('Deadline',compute='_get_deadline',inverse='_set_deadline')
    parent_task_id = fields.Many2one('syd_bpm.task_executed',string="Parent Task Executed")
    case_duration = fields.Float("Case Duration",compute="_case_duration")
    
    
    def _get_deadline(self):
        for a in self:
            if bool(a.process_id.date_deadline):
                for c in a.case_object_ids:
                    if c.process_object_id.id == a.process_id.date_deadline.id:
                        a.date_deadline = c.get_val()
                        return
            a.date_deadline = False
            
    
    
    def _set_deadline(self):
        for a in self:
            if bool(a.process_id.date_deadline):
                for c in a.case_object_ids:
                    if c.process_object_id.id == a.process_id.date_deadline.id:
                        c.set_val(a.date_deadline)
                
    
    
    def get_date_and_task(self):
        for case in self:
            date_task_start = False
            date_task_end = False
            task_active = ''
            for task in case.sudo().task_executed_ids :
                if (not date_task_start) : date_task_start = task.date_task_start
                if (not date_task_end and case.state=='completed') : 
                    date_task_end = task.date_task_end
                if task.date_task_start < date_task_start : date_task_start = task.date_task_start
                if (case.state=='completed') : 
                    if task.date_task_end > date_task_end : 
                        date_task_end = task.date_task_end
                if task.is_task_active :
                    if (task_active != '') : task_active +=", "
                    task_active += task.name + (" ("+task.user_id.name+")"  if task.user_id else '')
            case.date_task_start= date_task_start
            case.date_task_end = date_task_end
            case.task_active = task_active
                    
        
        
    @api.model
    def create(self, values):
        case =  super(Case, self).create(values)
        # nel caso in cui il processo venga cancellato voglio sapere quale processo era di questo case
        case.process_name = case.process_id.name
        for po in case.process_id.process_object_ids :
            case_object = self.env['syd_bpm.case_object'].create({
                                                    'process_object_id':po.id,
                                                    'case_id':case.id
                                                    })
            if po.is_attachment and not po.default_attachment:
                attachment = self.env['ir.attachment'].create({
                    'name': case.process_name + "_" + str(case_object.id)
                })
                
                case_object.set_val(attachment)
                 
        return case
    
        
    def cancel_case(self):
        self.ensure_one()
        for te in self.task_executed_ids:
            if not bool(te.date_task_end):
                if te.note_id:
                    te.is_task_active = False
                    te.note_id.unlink()
        self.state = 'cancelled'
        self.process_group_id._cancel_case(self)
        return True
        
    
    def _case_duration(self):
        for case in self:
            duration = 0.0
            
            for task_executed in case.task_executed_ids:
                if bool(task_executed.task_duration):
                    duration = duration + task_executed.task_duration
            
            #if duration > 0.0:
            case.case_duration = duration
            
                

class TaskExecuted(models.Model):
    _name = 'syd_bpm.task_executed'
    _description = 'Task executed'
    
    name = fields.Char(string='Name',required=True)
    user_id = fields.Many2one('res.users',string='User',related='note_id.user_id')
    is_task_active = fields.Boolean('Is Active')
    automated = fields.Boolean('Automated')
    date_task_start = fields.Datetime('Date Start')
    date_task_end = fields.Datetime('Date End')
    case_id = fields.Many2one('syd_bpm.case',string='Case',required=True,store=True)
    note_id = fields.Many2one('note.note',string='Note')
    process_id = fields.Many2one('syd_bpm.process',string='Process',related='case_id.process_id',store=True)
    sub_case_id = fields.Many2one('syd_bpm.case',string='Case of Subprocess')
    activity_id = fields.Many2one('syd_bpm.activity',string='Activity',required=True)
    process_group_id = fields.Many2one('syd_bpm.process_group',string='Process Group',related='process_id.process_group_id')
    task_duration = fields.Float("Task Duration",group_operator = 'avg')
    
     
    def _val_sub_process(self):
        self.ensure_one()
        task_executed_id = self 
        return {
                'project_id':task_executed_id.case_id.project_id.id,
                'name':_('Subprocess of %s - %s - %s') % (task_executed_id.process_id.name,task_executed_id.case_id.name, task_executed_id.name),
                'user_id':task_executed_id.case_id.user_id.id,
                'detail':task_executed_id.case_id.detail,
                 'parent_task_id' :task_executed_id.id 
                 } 
    
    def _val_note(self,user_id):
        self.ensure_one()
        task_executed_id = self 
        return {
            'name':' [%s] %s - %s ' % (task_executed_id.case_id.name, task_executed_id.activity_id.name,task_executed_id.process_id.name),
            'memo':' %s <br /><hr /> %s <hr /> %s ' %
                    ((task_executed_id.activity_id.description if task_executed_id.activity_id.description else ''),
                     task_executed_id.case_id.detail if task_executed_id.case_id.detail else '',
                     task_executed_id.process_id.description if task_executed_id.process_id.description else ''),
            'user_id': user_id,
            'case_id':task_executed_id.case_id.id,                                        
        }
         
                                                  
    @api.model
    def create(self, values):
        """ 
           In this method you manage all the activity type 
        """
        task_executed_id =  super(TaskExecuted, self).create(values)
        user_id = False
        activity_id = task_executed_id.activity_id
        if activity_id.user_id : user_id = activity_id.user_id.id 
        if activity_id.type == 'user-case' :
            user_id =task_executed_id.case_id.user_id.id
        elif (activity_id.type == 'dynamic-user') :
            for case_object_id in task_executed_id.case_id.case_object_ids:
                if case_object_id.process_object_id.id == activity_id.dynamic_user_id.id:
                    user_id = case_object_id.get_val()
        elif (activity_id.type == 'process-role') :
            user_id = activity_id.process_role_activity_id.get_user()
        if (activity_id.type == 'sub-process') :
            process_start = self.env['syd_bpm.process_start'].create(task_executed_id._val_sub_process())
            case_id = process_start.process_start(activity_id.sub_process_id)
            task_executed_id.sub_case_id = case_id.id
        elif (activity_id.type != 'automated'):
            note = self.env['note.note'].create(task_executed_id._val_note(user_id))
            task_executed_id.note_id = note.id
        else :
            activity_id.sudo().with_context({'case':task_executed_id.case_id}).action.run()
            task_executed_id.automated=True
            self.process_group_id._route_case_from_task(task_executed_id)
        return task_executed_id
    
    
    
    def write(self, values):
        return super(TaskExecuted, self).write(values)
    
    
    @api.constrains('date_task_end')
    def _task_duration(self):
        for task in self:
            if bool(task.date_task_start) and bool(task.date_task_end):
                
                date_diff_in_seconds = (task.date_task_end - task.date_task_start).seconds
                task.task_duration = date_diff_in_seconds / float(3600)
                                  

