#!/usr/bin/env python3
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
#     Santiago Dueñas <sduenas@bitergia.com>
#

import dateutil
import json
from grimoirelab.toolkit.datetime import str_to_datetime, datetime_utcnow


def json_date_handler(obj):
    """ Handle dates in JSON for beautifying purposes
    """
    if isinstance(obj, dateutil.tz.tzoffset):
        return str(dateutil.tz.tzoffset)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return str(obj)


class ElementMetadata:
    def __init__(self):
        self.uuid = None
        self.parent_uuid = None
        self.raw_uuid = None
        self.perceval_updated_on_ts = None
        self.model_version = None
        self.type = None
        self.subtype = None
        self.origin = None
        self.tag = None
        self.backend_version = None
        self.retrieval_ts = None
        self.processed_ts = None
        self.arthur_job_id = None
        # TODO: check self.fingerprint = None

    def __str__(self):
        return str(self.__dict__)


class Element:
    def __init__(self):
        self.metadata = None
        self.data = None
        self.data_ext = None

    def __str__(self):
        obj = {
            "metadata": self.metadata,
            "data": self.data,
            "data_ext": self.data_ext
        }
        return json.dumps(obj, sort_keys=True, indent=4,
                          default=json_date_handler)


class Commit(Element):
    def __init__(self):
        super().__init__()
        self.data_ext = {}
        self.data_ext['added_lines'] = None
        self.data_ext['removed_lines'] = None
        self.data_ext['changed_lines'] = None
        self.data_ext['num_files'] = None


class CommitAction(Element):
    def __init__(self):
        super().__init__()
