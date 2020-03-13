###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Archive 
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used 
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased 
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the 
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################

import os
import time
import hmac
import hashlib
import logging

from odoo.http import request

from odoo.addons.muk_utils.tests import common

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class ControllerTestCase(common.HttpCase):
    
    def setUp(self):
        super(ControllerTestCase, self).setUp()

    def tearDown(self):
        super(ControllerTestCase, self).tearDown()
    
    def test_archive_record_attachments(self):
        self.authenticate('admin', 'admin')
        domain = [
            ['type', '=', 'binary'],
            ['res_model', '!=', False], 
            ['res_field', '!=', False],
            ['res_id', '!=', 0]
        ]
        attachment = self.env['ir.attachment'].sudo().search(domain, limit=1)
        data={'model': attachment.res_model, 'id': attachment.res_id}
        self.assertTrue(self.url_open('/archive/record/attachments', data=data, csrf=True))
        
    def test_archive_records_attachments(self):
        self.authenticate('admin', 'admin')
        domain = [
            ['type', '=', 'binary'],
            ['res_model', '!=', 'res.partner'], 
            ['res_field', '!=', False],
            ['res_id', '!=', 0]
        ]
        attachment = self.env['ir.attachment'].sudo().search(domain, limit=2)
        data={'model': 'res.partner', 'ids[]': attachment.mapped('res_id')}
        self.assertTrue(self.url_open('/archive/records/attachments', data=data, csrf=True))
        
    def test_archive_attachments(self):
        self.authenticate('admin', 'admin')
        domain = [['type', '=', 'binary']]
        attachments = self.env['ir.attachment'].sudo().search(domain, limit=3)
        data={'ids[]': attachments.ids}
        self.assertTrue(self.url_open('/archive/attachments', data=data, csrf=True))