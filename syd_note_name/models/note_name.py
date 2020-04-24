# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Note(models.Model):
    _inherit = ['note.note']
    
    name = fields.Char('Name')
    
    
    @api.constrains('memo')
    def _generate_name(self):
        """ Read the first line of the memo to determine the note name """
        for note in self:
            if not note.name:
                super(Note,self)._compute_name()
