# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools import html2plaintext

class Note(models.Model):
    _inherit = ['note.note']
    
    
    
    pm_del_index = fields.Integer('Delegation Index')
    
    
        