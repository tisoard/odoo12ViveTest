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
import uuid
import base64
import shutil
import logging
import tempfile
import mimetypes

from itertools import groupby
from contextlib import closing

from odoo import api, models

from odoo.addons.muk_utils.tools.file import slugify, unique_name
from odoo.addons.muk_archive.tools.archive import archive

_logger = logging.getLogger(__name__)

class ArchiveAttachment(models.Model):
   
    _inherit = 'ir.attachment'
    
    @api.multi
    def archive(self, name=None, format="zip", export="binary"):
        unames = []
        if not name:
            name = uuid.uuid4().hex
        tmp_dir = tempfile.mkdtemp()
        try:
            base_dir = os.path.join(tmp_dir, name)
            os.mkdir(base_dir)
            for attach in self.filtered(lambda rec: rec.type == "binary" and rec.datas):
                uname = unique_name(attach.datas_fname or uuid.uuid4().hex, unames, escape_suffix=True)
                unames.append(uname)
                file_path = os.path.join(base_dir, uname)
                with closing(open(file_path, 'wb')) as writer:
                    writer.write(base64.b64decode(attach.with_context({}).datas))    
            return archive(base_dir, tmp_dir, name, format, export)
        finally:
            shutil.rmtree(tmp_dir)
            
    @api.multi
    def archive_with_structure(self, name=None, format="zip", export="binary"):
        attachments = self.filtered(lambda rec: rec.type == "binary" and rec.datas) 
        structure = groupby(attachments, lambda attach: (attach.res_id, attach.res_name))
        if not name:
            name = uuid.uuid4().hex
        tmp_dir = tempfile.mkdtemp()
        try:
            base_dir = os.path.join(tmp_dir, name)
            os.mkdir(base_dir)
            for record, attachments in structure:
                dir_name = "%s_%s" % (record[0], slugify(record[1])) if record[1] else uuid.uuid4().hex
                rec_dir = os.path.join(base_dir, dir_name)
                os.mkdir(rec_dir)
                unames = []
                for attach in attachments:
                    uname = uuid.uuid4().hex
                    if attach.datas_fname:
                        uname = unique_name(attach.datas_fname, unames, escape_suffix=True)
                    elif attach.mimetype:
                        uname = "%s%s" % (uname, mimetypes.guess_extension(attach.mimetype))
                    unames.append(uname)
                    file_path = os.path.join(rec_dir, uname)
                    with closing(open(file_path, 'wb')) as writer:
                        writer.write(base64.b64decode(attach.with_context({}).datas))    
            return archive(base_dir, tmp_dir, name, format, export)
        finally:
            shutil.rmtree(tmp_dir) 
