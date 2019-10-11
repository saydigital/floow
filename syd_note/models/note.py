# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools import html2plaintext

class Note(models.Model):
    _inherit = ['note.note']
    
    active=fields.Boolean('Active ', help="If the active field is set to False, it will allow you to hide the note without removing it.",default=True)



    @api.multi
    def archive_note(self):
        self.write({'active': False})
        
    @api.model
    def archive_completed_notes(self,ids=None):
        to_complete = self.env['note.note'].search([('open','=',False)])
        for note in to_complete:
            note.archive_note()