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
import shutil
import logging
import tempfile

from contextlib import closing

from odoo.addons.muk_utils.tools.file import unique_files

_logger = logging.getLogger(__name__)

def archive(base_dir, root_dir, name, format="zip", export="binary"):
    """
    Archive a directory.
    
    :param base_dir: The directory, which has to be archvied. 
    :param root_dir: The root directory.
    :param name: The name of the archive.
    :param format: The archive format (zip, tar, gztar, bztar, xztar).
    :param export: The output format (binary, file, base64).
    :return: Returns the output depending on the given export.
    """
    archive_path = os.path.join(root_dir, "%s.%s" % (name, format))
    shutil.make_archive(base_dir, format, root_dir, name)
    with closing(open(archive_path, 'rb')) as file:
        if export == 'file':
            output = io.BytesIO()
            output.write(file.read())
            output.close()
            return output
        elif export == 'base64':
            return base64.b64encode(file.read())
        else:
            return file.read()

def archive_files(files, name=None, format="zip", export="binary"):
    """
    Archive a list of files.
    
    :param files: The list of files. A file is a tuple consisting of filename and binary.
    :param name: The name of the archive.
    :param format: The archive format (zip, tar, gztar, bztar, xztar).
    :param export: The output format (binary, file, base64).
    :return: Returns the output depending on the given export.
    """
    files = unique_files(files)
    tmp_dir = tempfile.mkdtemp()
    name = name or uuid.uuid4().hex
    try:
        base_dir = os.path.join(tmp_dir, name)
        os.mkdir(base_dir)
        for file in files:
            file_path = os.path.join(base_dir, file[0])
            with closing(open(file_path, 'wb')) as writer:
                writer.write(file[1])    
        return archive(base_dir, tmp_dir, name, format, export)
    finally:
        shutil.rmtree(tmp_dir)