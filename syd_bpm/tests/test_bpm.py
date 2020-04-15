# -*- coding: utf-8 -*-
# Copyright 2018-2019 SayDigital (https://www.saydigital.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

class TestBpm(common.SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestBpm, cls).setUpClass()

        user_group_bpm = cls.env.ref('syd_bpm.group_bpm_manager')
        

        

        # Test users to use through the various tests
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_bpm = Users.create({
            'name': 'Jack Bpm',
            'login': 'jack',
            'email': 'j.b@example.com',
            'signature': 'JackBpm',
            'notification_type': 'email',
            'groups_id': [(6, 0, [user_group_bpm.id])]})
        

        # Test 'Pigs' project
        cls.project_group = cls.env['syd_bpm.process_group'].with_context({'mail_create_nolog': True}).create({
            'name': 'PGTest',
            'description': 'PGTest'})
        # Already-existing tasks in Pigs
        cls.process_1 = cls.env['syd_bpm.process'].with_context({'mail_create_nolog': True}).create({
            'name': 'Process 1',
            'process_group_id': cls.project_group.id,
            'startable':True})
        cls.activity_1 = cls.env['syd_bpm.activity'].with_context({'mail_create_nolog': True}).create({
            'name': 'Act 1',
            'process_id': cls.process_1.id,
            'is_start_activity':True})
        cls.po_1 = cls.env['syd_bpm.process_object'].with_context({'mail_create_nolog': True}).create({
            'name': 'PO 1',
            'process_id': cls.process_1.id,
            'type':'char'

            })

    
    def test_dyn_form(self):
        """ ensure any users can create new users """
        self.dyn_1 = self.env['syd_bpm.dynamic_form'].with_context({'mail_create_nolog': True}).create({
            'name': 'DynForm',
            'process_id': self.process_1.id,
            'note':'DynForm',
            'dynamic_form_line_ids':{'string_field':'po_1','process_object_id':self.po_1.id}
            })
        self.activity_1.dynamic_form_id = self.dyn_1.id
        self.dyn_1.set_done()
        self.assertEqual(bool(self.dyn_1.dynamic_wizard_id), True,
            'Dyn Wizard not created')
        
