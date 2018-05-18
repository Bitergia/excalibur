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
#     Alberto Pérez García-Plaza <alpgarcia@bitergia.com>
#
from grimoirelab.toolkit.datetime import datetime_utcnow

from excalibur.data.spitfire.alloy import RefinedMetadata
from excalibur.tongs import Tongs


class Builder():

    # TODO dates should be stored in a common format, e.g. grimoire_creation_date vs refinement_ts

    UNKNOWN_VALUE = 'Unknown'

    def __init__(self, element):
        self.tongs = Tongs()
        self.element = element

    def process(self):
        raise NotImplementedError("process not defined")

    def _process_metadata(self):
        metadata = RefinedMetadata()
        # raw metadata
        metadata.uuid = self.element.uuid
        metadata.parent_uuid = self.element.parent_uuid
        metadata.raw_uuid = self.element.metadata.raw_uuid
        metadata.perceval_updated_on_ts = self.element.metadata.perceval_updated_on_ts
        metadata.model_version = self.element.metadata.model_version
        metadata.type = self.element.metadata.type
        metadata.subtype = self.element.metadata.subtype
        metadata.origin = self.element.metadata.origin
        metadata.tag = self.element.metadata.tag
        metadata.backend_version = self.element.metadata.backend_version
        metadata.retrieval_ts = self.element.metadata.retrieval_ts
        metadata.processed_ts = self.element.metadata.processed_ts
        metadata.arthur_job_id = self.element.metadata.arthur_job_id
        # Refined metadata
        metadata.grimoire_creation_date = self.element.metadata.perceval_updated_on_ts
        metadata.refinement_ts = datetime_utcnow()

        return metadata

    def _get_unique_identity(self, name, email, username):
        return self.tongs.retrieve_unique_identity(self.element.metadata.subtype,
                                                   name,
                                                   email,
                                                   username)
