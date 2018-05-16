# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

from copy import deepcopy
import hashlib
import logging

from grimoirelab.toolkit.datetime import datetime_utcnow

from excalibur.errors import HammerError
from excalibur.data.furnace.element import ElementMetadata


logger = logging.getLogger(__name__)


class Hammer:

    def __init__(self, raw_data, raw_metadata):
        self.num_elements = 0
        self.raw_data = raw_data
        self.raw_metadata = raw_metadata

    def smash(self):
        raise NotImplementedError("split not defined")

    def datemize(self, element):
        return element

    def modelize(self, element):
        return element

    def unify(self, element):
        return element

    def metadata(self, element):
        metadata = ElementMetadata()
        furnace_metadata = self.extract_metadata()

        metadata.raw_uuid = furnace_metadata['raw_uuid']
        metadata.perceval_updated_on_ts = furnace_metadata['perceval_updated_on_ts']
        metadata.subtype = furnace_metadata['subtype']
        metadata.origin = furnace_metadata['origin']
        metadata.tag = furnace_metadata['tag']
        metadata.backend_version = furnace_metadata['backend_version']
        metadata.retrieval_ts = furnace_metadata['retrieval_ts']
        metadata.arthur_job_id = furnace_metadata['arthur_job_id']

        metadata.processed_ts = datetime_utcnow()
        metadata.model_version = '0.1.0'
        metadata.type = type(element).__name__
        element.metadata = metadata

        return element

    def verify(self, element):
        if not element.uuid:
            msg = "No uuid for element %s" % str(element)
            raise HammerError(cause=msg)

        if not element.parent_uuid:
            msg = "No parent_uuid for element %s" % str(element)
            raise HammerError(cause=msg)

        return element

    def extract_metadata(self):
        furnace_metadata = {
            'raw_uuid': self.raw_metadata['uuid'],
            'perceval_updated_on_ts': self.raw_metadata['updated_on'],
            'subtype': self.raw_metadata['backend_name'],
            'origin': self.raw_metadata['origin'],
            'category': self.raw_metadata['category'],
            'tag': self.raw_metadata['tag'],
            'backend_version': self.raw_metadata['backend_version'],
            'retrieval_ts': self.raw_metadata['timestamp'],
            'arthur_job_id': None
        }
        return furnace_metadata

    @staticmethod
    def copy_data(data):
        replica = deepcopy(data)
        return replica

    @staticmethod
    def create_uuid(*args):
        s = ':'.join(str(a) for a in args)

        sha1 = hashlib.sha1(s.encode('utf-8', errors='surrogateescape'))
        uuid_sha1 = sha1.hexdigest()

        return uuid_sha1
