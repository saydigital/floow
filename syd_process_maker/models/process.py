# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
from ...syd_bpm.models.process import BPMInterface
import odoo.exceptions
import odoo
import requests
import json 
import time
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ProcessGroup(BPMInterface,models.Model):
    _inherit = 'syd_bpm.process_group'
    
    type= fields.Selection(selection_add=[("ProcessMaker2", "ProcessMaker2")])
   
    pm_url = fields.Char(string='PM Url',required=True)
    pm_workspace = fields.Char(string='PM Workspace',required=True)
    pm_client_id = fields.Char(string='PM Client Id',required=True)
    pm_client_secret = fields.Char(string='PM Client secret',required=True)
    pm_username = fields.Char(string='PM Username',required=True)
    pm_password = fields.Char(string='PM Password',required=True)
    
    pm_user_name = fields.Char(string='Nome of the user of PM',required=True)
    
    
    def _call(self,request,jsonobject=dict(),method='GET'):
        auth = {
                'grant_type': 'password',
                'scope': '*',
                'client_id': self.pm_client_id,
                'client_secret': self.pm_client_secret,
                'username': self.pm_username,
                'password': self.pm_password
        }
        result = requests.post(self.pm_url+"/"+self.pm_workspace+'/oauth2/token', data=auth)
        if (not result.ok  ):
            raise ValidationError('{}, {}'.format(result.status_code, result.text))
        jsonresult = json.loads(result.content)
        if ('error' in jsonresult) :
            raise ValidationError('{}'.format(result.error_description))
        access_token = jsonresult['access_token']
        
        headers = {'Authorization': 'Bearer '+access_token}
        
        endresult = ''
        if (method == 'GET'):
            endresult = requests.get(self.pm_url+'/api/1.0/'+self.pm_workspace+'/'+request,params =jsonobject,headers=headers )
        if (method == 'POST'):
            endresult = requests.post(self.pm_url+'/api/1.0/'+self.pm_workspace+'/'+request,data =jsonobject ,headers=headers)
        if (method == 'PUT'):
            endresult = requests.put(self.pm_url+'/api/1.0/'+self.pm_workspace+'/'+request,data =jsonobject ,headers=headers)
        if (not bool(endresult) or not endresult.ok):
            raise  Exception(str(endresult.status_code)+"-" + str(endresult.content))
        if bool(endresult.content): 
            if 'json' in endresult.headers['Content-Type']:
                return json.loads(endresult.content) 
            else :
                return endresult.content
        else: 
            return False
    
    @api.model
    def _get_process_list(self):
        process_list = self._call('project')
        return process_list
    
    @api.model
    def _get_activity_list(self,process_id):
        process_definition = self._call('project/'+process_id)
        tasks = process_definition['diagrams'][0]['activities']
        return tasks
    
    @api.model
    def _get_starting_activity(self,process_id):
        # GET /case/start-cases
        starting_activities = self._call('project/%s/starting-tasks' %process_id )
        return starting_activities
        
    
        
    @api.model
    def _route_case(self,case_id,del_index=False):
        # PUT /cases/{app_uid}/route-case
        
        par = dict()
        if (del_index) : par['del_index'] = del_index
        res =self._call('cases/'+case_id+'/route-case',par,method='PUT')
        
        return True
    
    @api.model
    def _get_current_tasks(self,case):
        #GET cases/{app_uid}/tasks
        #GET /cases/{app_uid}/tasks
        case_id = case['app_uid']
        res =self._call('cases/'+case_id+'/tasks')
        tasklist = []
        if isinstance(res, dict):
            res = [res]
        for task in res :
            if task['status'] in ['TASK_IN_PROGRESS','TASK_PARALLEL'] :
                if (len(task['delegations']) > 0 ):
                    index = 0
                    for ele in task['delegations']:
                        if ele['del_finish_date'] == 'Not finished':
                            break
                        index = index + 1
                    task['del_index'] = task['delegations'][index]['del_index']
                tasklist.insert(0,task)
        return tasklist
    
    
    @api.model
    def _get_process_map(self,process_id):
        #GET /light/process/{pro_uid}/case
        res = self._call('light/process/'+process_id+'/case')
        return res;
      
      
    @api.model
    def _get_case_variables(self,case_id):
        #GET /cases/{app_uid}/variables
        res = self._call('cases/'+case_id+'/variables')
        variable_list = []
        for v in res :
            if (v not in ["SYS_LANG","SYS_SKIN","SYS_SYS","APPLICATION","PROCESS","TASK","INDEX","USER_LOGGED","USR_USERNAME","PIN","APP_NUMBER"]):  
                 variable_list.insert(0,v)
        return variable_list                
     
    @api.model
    def _set_case_variables(self,case_id,data):
        #PUT /cases/{app_uid}/variable   
        res = self._call('cases/'+case_id+'/variable',data,method='PUT')
        return res;
        
    @api.model
    def _get_process_variables(self,process_id):
        #GET /api/1.0/{workspace}/project/{prj_uid}/process-variables
        res = self._call('project/'+process_id+'/process-variables')
        return res
    
    @api.model
    def _get_case_info(self,case_id):
        #GET /cases/{app_uid}
        res = self._call('case/'+case_id)
        return res
    
    @api.model
    def _get_activity_info(self,process_id,activity_id):
        #GET /api/1.0/{workspace}/project/{prj_uid}/activity/{act_uid}
        res = self._call('project/'+process_id+'/activity/'+activity_id)
        return res
    
    @api.model
    def _get_category_info(self,cat_id):
        #GET /project/category/{cat_uid}
        res = self._call('project/category/%s'%(cat_id))
        return res
    
    @api.model
    def _get_assign_user(self):
        par = dict()
        par['filter'] = self.pm_user_name
        res = self._call('users',par)
        try:
            return res[0]['usr_uid']
        except :
            raise ValidationError(_('No ProcessMaker user to assign task'))
        
        
    @api.model
    def _get_user_of_task(self,process_id,task_id):
        res = self._call('project/%s/activity/%s/assignee'%(process_id,task_id))
        return res
    
    @api.model
    def _assign_user_to_task(self,process_id,task_id,user_id):
        #/project/{prj_uid}/activity/{act_uid}/assignee
        par = dict()
        par['aas_uid'] = user_id
        par['aas_type'] ='user'
        res = self._call('project/%s/activity/%s/assignee'%(process_id,task_id),par,method='POST')
        return res
    
    
    @api.model
    def _cancel_case(self,case_id):
        #/cases/{app_uid}/cancel
        res = self._call('cases/%s/cancel'%(case_id.pm_case_id),method='PUT')
        return res
    
    
    
    def start_process(self,process_id,activity_id):
        # POST /cases
        self.ensure_one()
        pm_process_id = process_id.pm_process_id
        pm_activity_id = activity_id.pm_activity_id
        par = dict()
        par['pro_uid'] = pm_process_id
        par['tas_uid'] = pm_activity_id
        res = self._call('cases',par,method='POST')
        
        return res
    
    
    def update_processes(self):
        for pgroup in self:
            pm_user_id = self._get_assign_user()
            
            
            process_list = self._get_process_list()
            for process in process_list :
                process_id = self.env['syd_bpm.process'].search([('pm_process_id','=',process['prj_uid'])],limit=1)
                if (not process_id or not process_id.locked):
#                     map = self._get_process_map(process['prj_uid'])
                    pm_category = False
                    if process['prj_category'] != '':
                        pm_category = self._get_category_info(process['prj_category'])['cat_name']
                    if (not process_id) :
                        process_id = self.env['syd_bpm.process'].create(
                                                           {'name':process['prj_name'],
                                                            'description':process['prj_description'],
                                                            'pm_process_id':process['prj_uid'],
                                                            'process_group_id':pgroup.id,
                                                            'category_id':self.env['syd_bpm.process_category'].get_or_create_category(pm_category)
                                                            }
                                                           )
                    else :
                        process_id.name=process['prj_name']
                        process_id.description = process['prj_description']
                        process_id.category_id=self.env['syd_bpm.process_category'].get_or_create_category(pm_category)

                        
#                     img =  '<img src="data:image/png;base64,{0}" />'.format(map['map'])
                        #problemi immagine
                        #process_id.map = img
#                     self.env.cr.execute("UPDATE syd_bpm_process set map = '%s' where id = %d" % (img,process_id.id))
    
                           
                    activity_list = self._get_activity_list(process_id.pm_process_id)
                    act_not_to_delete = []
                    for activity in activity_list :
                        
                        activity_id = self.env['syd_bpm.activity'].search([('pm_activity_id','=',activity['act_uid'])],limit=1)
                        
                        activity_info = self._get_activity_info(process_id.pm_process_id,activity['act_uid'])
                        if (not activity_id) :
                            activity_id = self.env['syd_bpm.activity'].create(
                                                           {'name':activity['act_name'],
                                                            'description' : activity_info['properties']['tas_description'],
                                                            'process_id':process_id.id,
                                                            'pm_activity_id':activity['act_uid']
                                                            }
                                                           )
                        else :
                            activity_id.name = activity['act_name']
                            activity_id.description = activity_info['properties']['tas_description']
                            activity_id.is_start_activity = False
                        
                        # Assign to a pm user the task if it is unassigned
                        users = self._get_user_of_task(process_id.pm_process_id,activity['act_uid'])
                        if not (bool(users)):
                            self._assign_user_to_task(process_id.pm_process_id,activity['act_uid'],pm_user_id)
                        act_not_to_delete.insert(0,activity_id.id)
                    act_to_delete = self.env['syd_bpm.activity'].search([('process_id','=',process_id.id),('id','not in',act_not_to_delete)])
                    for act in act_to_delete:
                        act.deprecated = True
                        
                    process_variables = self._get_process_variables(process_id.pm_process_id)
                    var_not_to_delete = []
                    for pvariable in process_variables:
                        process_object_id = self.env['syd_bpm.process_object'].search([('pm_variable_id','=',pvariable['var_uid'])],limit=1)
                        if (not process_object_id) :
                            self.env['syd_bpm.process_object'].create({
                                                                 'name':pvariable['var_name'],
                                                                 'pm_variable_id':pvariable['var_uid'],
                                                                 'pm_accepted_values':pvariable['var_accepted_values'],
                                                                 'process_id':process_id.id,
                                                                 'pm_type':pvariable['var_field_type']
                                                                 })
                            process_object_id = self.env['syd_bpm.process_object'].search([('pm_variable_id','=',pvariable['var_uid'])],limit=1)
                        else :
                            process_object_id.name = pvariable['var_name']
                            process_object_id.pm_accepted_values = pvariable['var_accepted_values']
                            process_object_id.pm_type = pvariable['var_field_type']
                            
                        var_not_to_delete.insert(0,process_object_id.id)
                    for pv in self.env['syd_bpm.process_object'].search([('process_id','=','process_id.id'),('id','not in',var_not_to_delete)]):
                        pv.deprecated = True
                starting_activities = self._get_starting_activity(process_id.pm_process_id)
                for activity in starting_activities :
                    act = self.env['syd_bpm.activity'].search([('pm_activity_id','=',activity['act_uid'])],limit=1)
                    act.is_start_activity = True
                    acts = self.env['syd_bpm.activity'].search([('process_id','=',process_id.id),('is_start_activity','=',True)])
                    if (not starting_activities ) :
                        process.startable = False
                        acts.is_start_activity = False
            pgroup.last_update = fields.Datetime.now()
            return True
    
    @api.model
    def _set_variables(self,case):
            # Da capire cosa succede per i sottoprocessi se setti una variabile del padre
            data = {}
            flag = False
            for v in case.case_object_ids :
                if bool(v.process_object_id.pm_variable_id):
                    data[v.name] = v.get_val()
                    flag=True
            if flag: 
                case.process_group_id._set_case_variables(case.pm_case_id,data)
            
    @api.model
    def _route_case_from_task(self,task_executed_id):
            case = task_executed_id.case_id
            case.sudo().process_group_id._set_variables(case)
            case_info =  case.process_group_id._get_case_info(case.pm_case_id)
            if (case_info['app_status']=='COMPLETED' and  case.state == 'in_progress') :
                case.state = 'completed'
                if (case.parent_id) :
                    case.process_group_id._route_case_from_task(case.parent_task_id)
            else :
                current_tasks_pre = case.process_group_id._get_current_tasks(case_info)
                cid_pre = [ctask['tas_uid'] for ctask in current_tasks_pre]
               
                if (case.process_group_id._route_case(case.pm_case_id,task_executed_id.pm_del_index)) :
                        current_tasks_post = case.process_group_id._get_current_tasks(case_info)
                        cid_post = [ctask['tas_uid'] for ctask in current_tasks_post] 
                        for current_task in current_tasks_post :
                            activity_id = self.env['syd_bpm.activity'].search([('pm_activity_id','=',current_task['tas_uid'])])
                            task_id = self.env['syd_bpm.task_executed'].search([('case_id','=',case.id),('pm_task_id','=',current_task['tas_uid']),('pm_del_index','=',current_task['del_index'])])
                            # per risolvere loop e task paralleli
                            if (not bool(task_id)):
                                self.env['syd_bpm.task_executed'].create(
                                                    {
                                                     'name':current_task['tas_title'],
                                                     'pm_task_id':current_task['tas_uid'],
                                                     'pm_del_index':current_task['del_index'],
                                                     'is_task_active' : True,
                                                     'case_id':case.id,
                                                     'date_task_start' : fields.Datetime.now(),
                                                     'activity_id' :activity_id.id
                                                     }
                                                    )
                        for current_task in current_tasks_pre :
                                # Task completati
                            if (current_task['tas_uid'] not in cid_post):
                                task_completed = self.env['syd_bpm.task_executed'].search([('pm_task_id','=',current_task['tas_uid']),('case_id','=',case.id,)],limit=1)
                                # TODO
                                task_completed.is_task_active=False
                                task_completed.date_task_end=fields.Datetime.now()
                    
                
                
                case_info =  case.process_group_id._get_case_info(case.pm_case_id)
                ## Ad esempio dopo azioni automatiche 
                if (case_info['app_status']=='COMPLETED' and case.state == 'in_progress') :
                    case.state = 'completed'
                    if (case.parent_id) :
                        case.process_group_id._route_case_from_task(case.parent_task_id)    
    
           
class Process(models.Model):
    _inherit = 'syd_bpm.process'
    
    
    pm_process_id = fields.Char(string='Process Maker ID',required=False) 


   
class Activity(models.Model):
    _inherit = 'syd_bpm.activity'
    
    
    
    pm_activity_id = fields.Char(string='Process Maker ID',required=False)
    
    
class Case(models.Model):
    _inherit = 'syd_bpm.case'
    
    
    pm_case_id = fields.Char(string='Process Maker ID',required=False)
   
    
    
                 

class TaskExecuted(models.Model):
    _inherit = 'syd_bpm.task_executed'
    
    
    
    pm_task_id = fields.Char('Activity Id')
    pm_del_index = fields.Integer('Del Index')
    
                                           
    
    def _val_note(self,user_id):
        res = super(TaskExecuted,self)._val_note(user_id)                                          
        res['pm_del_index'] = self.pm_del_index
        return res
    
   
    
    

    

    