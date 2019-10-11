# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
import time
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import random

class ProcessRoleUser(models.Model):
    _name = 'syd_bpm.process_role_user'
    _description = 'Business Process Manager Role'
    _order = 'sequence'
    
    name = fields.Char(related="user_id.name")
    user_id = fields.Many2one('res.users',string="User",required=True)
    sequence = fields.Integer(string='Sequence')
    process_role_id = fields.Many2one('syd_bpm.process_role',string="Process Role")
    
class ProcessRole(models.Model):
    _name = 'syd_bpm.process_role'
    _description = 'Business Process Manager Role'

    
    name = fields.Char(string='Name',required=True)
    process_user_ids = fields.One2many('syd_bpm.process_role_user','process_role_id',string="Users")
    process_id = fields.Many2one('syd_bpm.process',string='Process')
    
class ProcessRoleActivity(models.Model):
    _name = 'syd_bpm.process_role_activity'
    _description = 'Business Process Manager Role Activity'

    
    name = fields.Char(string='Name',related="process_role_id.name")
    process_role_id = fields.Many2one('syd_bpm.process_role',string="Process Role")
    activity_id = fields.Many2one('syd_bpm.activity',string="Activity")
    type = fields.Selection([
                ('random', "Random"),
                ('less-activity',"User with less process activity"),
                ('first-of-role',"First of Role")
            ], default='first-of-role',track_visibility='onchange',required=True)
    
    @api.multi
    def get_user(self):
        self.ensure_one()
        self = self.sudo()
        users = [u.user_id.id for u in self.process_role_id.process_user_ids ]
        if (self.type == 'random'):
            return random.choice(users)
        elif (self.type == 'less-activity'):
            min = False;
            user = False
            for a in users:
                temp = self.env['note.note'].search_count([('user_id','=',a),('active','=',True),('process_id','!=',False)])
                if min == False or temp <= min:
                    min = temp
                    user = a
            return user
        elif (self.type == 'first-of-role'):
            return users[0]