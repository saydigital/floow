# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api
from odoo.tools.translate import _
import time
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class ProcessDateCalculated(models.Model):
    _name = 'syd_bpm.process_date_calculated'
    _description = 'Process Date Term'

    
    name = fields.Char(string='Name',required=True)
    days = fields.Integer(string='Number of Days', required=True, default=0)
    option = fields.Selection([
            ('day_after_date', 'Day(s) after the Date'),
            ('fix_day_following_month', 'Day(s) after the end of the date month'),
            ('last_day_following_month', 'Last day of following month'),
            ('last_day_current_month', 'Last day of current month'),
        ],
        default='day_after_date', required=True, string='Options'
        )
    
    
    def compute(self, date_ref=False):
        """ 
           Compute the date based on the options
        """
        date_ref = date_ref or fields.Date.today()
        result = []
        
        next_date = fields.Date.from_string(date_ref)
        if self.option == 'day_after_date':
                next_date += relativedelta(days=self.days)
        elif self.option == 'fix_day_following_month':
            next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
            next_date = next_first_date + relativedelta(days=self.days - 1)
        elif self.option == 'last_day_following_month':
            next_date += relativedelta(day=31, months=1)  # Getting last day of next month
        elif line.option == 'last_day_current_month':
            next_date += relativedelta(day=31, months=0)  # Getting last day of next month
        result=fields.Date.to_string(next_date)
       
        return result
    
    
