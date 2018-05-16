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

import json


def json_date_handler(obj):
    """Handle dates in JSON for beautifying purposes"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return str(obj)


class ElementMetadata:
    def __init__(self):
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

    def to_dict(self):
        obj = {
            'raw_uuid': self.raw_uuid,
            'perceval_updated_on_ts': self.perceval_updated_on_ts,
            'model_version': self.model_version,
            'type': self.type,
            'subtype': self.subtype,
            'origin': self.origin,
            'tag': self.tag,
            'backend_version': self.backend_version,
            'retrieval_ts': self.retrieval_ts,
            'processed_ts': self.processed_ts.isoformat(),
            'arthur_job_id': self.arthur_job_id
        }

        return obj


class Element:
    def __init__(self, **kwargs):
        self.metadata = {}
        self.data = {}
        self.data_ext = {}
        self.uuid = None
        self.parent_uuid = None

    def __str__(self):
        obj = {
            "metadata": self.metadata.to_dict(),
            "uuid": self.uuid,
            "parent_uuid": self.parent_uuid,
            "data": self.data,
            "data_ext": self.data_ext
        }
        return json.dumps(obj, sort_keys=True, indent=4,
                          default=json_date_handler)


class Commit(Element):
    def __init__(self):
        super().__init__()
        self.data_ext['added_lines'] = None
        self.data_ext['removed_lines'] = None
        self.data_ext['changed_lines'] = None
        self.data_ext['num_files'] = None
        self.data_ext['is_merge'] = None


class CommitAction(Element):
    def __init__(self):
        super().__init__()


class Issue(Element):
    def __init__(self):
        super().__init__()


class IssueComment(Element):
    def __init__(self):
        super().__init__()


class IssueJournal(Element):
    def __init__(self):
        super().__init__()


class IssueReaction(Element):
    def __init__(self):
        super().__init__()


class User(Element):
    def __init__(self, username=None, email=None, name=None):
        super().__init__()
        self.data['username'] = username
        self.data['email'] = email
        self.data['name'] = name

    def digest(self):
        return ':'.join([str(self.data['username']),
                         str(self.data['email']),
                         str(self.data['name'])])
