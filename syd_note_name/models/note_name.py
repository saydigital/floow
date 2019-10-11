# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Note(models.Model):
    _inherit = ['note.note']
    
    name = fields.Char('Name')