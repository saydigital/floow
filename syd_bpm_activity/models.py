# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools import html2plaintext
from odoo.exceptions import ValidationError


    
    
    
    
class Note(models.Model):
    _inherit = 'note.note'
    
    @api.model
    def create(self, values):
        res = super(Note,self).create(values)
        if bool(res.case_id):
            date_deadline = fields.Date.today() if not res.date_deadline else res.date_deadline
            model_id = self.env['ir.model'].search([('model','=','note.note')])
            activity_type_id = self.env['ir.config_parameter'].get_param('syd_bpm.activity_type_id')
            if not bool(activity_type_id):
                raise ValidationError('Default Activity Type is not defined. Contact the Administrator')
            self.env['mail.activity'].create({
                                              'date_deadline':date_deadline,
                                              'user_id':res.user_id.id,
                                              'res_model_id':model_id.id,
                                              'res_id':res.id,
                                              'activity_type_id':activity_type_id,
                                              'note':res.memo,
                                              'summary':res.name
                                              })
        return res