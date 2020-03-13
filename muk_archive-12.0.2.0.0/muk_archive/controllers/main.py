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

import uuid
import logging

from werkzeug.exceptions import BadRequest

from odoo import _, http
from odoo.http import request

from odoo.addons.muk_utils.tools.http import request_params

_logger = logging.getLogger(__name__)

class ArchiveController(http.Controller):

    @http.route([
        '/archive/record/attachments',
        '/archive/record/attachments/<string:model>',
        '/archive/record/attachments/<string:model>/<int:id>',
        '/archive/record/attachments/<string:model>/<int:id>/<string:name>',
        '/archive/record/attachments/<string:model>/<int:id>/<string:name>/<string:format>'
    ], type='http', auth="user")
    def archive_record_attachments(self, model, id, name=None, format="zip", **kw):
        domain = [
            '&', ['res_model', '=', model], 
            '&', ['res_id', '=', id],
            '|', ['res_field', '=', False], ['res_field', '!=', False] 
        ]
        attachments = request.env['ir.attachment'].search(domain)
        if len(attachments):
            name = name or model
            content = attachments.archive(name, format)
            headers = [('Content-Type', 'application/zip' if format == "zip" else 'application/x-tar'),
                ('Content-Disposition', http.content_disposition("%s.%s" % (name, format))),
                ('Content-Length', len(content))]
            return request.make_response(content, headers)
        else:
            return request.not_found()

    @http.route([
        '/archive/records/attachments',
        '/archive/records/attachments/<string:model>',
        '/archive/records/attachments/<string:model>/<string:name>',
        '/archive/records/attachments/<string:model>/<string:name>/<string:format>'
    ], type='http', auth="user")
    def archive_records_attachments(self, model, name=None, format="zip", **kw):
        attachments_ids = request_params(request.httprequest).getlist('ids[]', None)
        if attachments_ids:
            domain = [
                '&', ['res_model', '=', model], 
                '&', ['res_id', 'in', list(map(int, attachments_ids))],
                '|', ['res_field', '=', False], ['res_field', '!=', False] 
            ]
            attachments = request.env['ir.attachment'].search(domain)
            if len(attachments):
                name = name or model
                content = attachments.archive_with_structure(name, format)
                headers = [('Content-Type', 'application/zip' if format == "zip" else 'application/x-tar'),
                    ('Content-Disposition', http.content_disposition("%s.%s" % (name, format))),
                    ('Content-Length', len(content))]
                return request.make_response(content, headers)
            else:
                return request.not_found()
        else:
            raise BadRequest(_("Parameter ids[] is missing!"))

    @http.route([
        '/archive/attachments',
        '/archive/attachments/<string:name>',
        '/archive/attachments/<string:name>/<string:format>',
    ], type='http', auth="user")
    def archive_attachments(self, name=None, format="zip", **kw):
        param_ids = request_params(request.httprequest).getlist('ids[]')
        attachments = request.env['ir.attachment'].browse(map(int, param_ids))
        if attachments.exists():
            name = name or uuid.uuid4().hex
            content = attachments.archive_with_structure(name, format)
            headers = [('Content-Type', 'application/zip' if format == "zip" else 'application/x-tar'),
                ('Content-Disposition', http.content_disposition("%s.%s" % (name, format))),
                ('Content-Length', len(content))]
            return request.make_response(content, headers)
        else:
            return request.not_found()