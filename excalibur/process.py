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

class CornerStoneMetadata:
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

def json_date_handler(obj):
    """ Handle dates in JSON for beautifying purposes
    """
    if isinstance(obj, dateutil.tz.tzoffset):
        return str(dateutil.tz.tzoffset)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return str(obj)

class CornerStoneItem:
    def __init__(self):
        self.metadata = None
        self.data = None
        self.data_ext = None

    def __str__(self):
        d = {
            "metadata": self.metadata,
            "data": self.data
        }
        return json.dumps(d, sort_keys=True, indent=4,
                          default=json_date_handler)


def generate_uuid(item, uuid_metadata, cs_type):
    if cs_type == "commit":
        return uuid_metadata['raw_uuid'] # TODO: generate a real UUID
    elif cs_type == "commit_action":
        return uuid_metadata['parent_uuid'] + item['file']
    else:
        raise TypeError("Invalid type %s", cs_type)


def process(raw_items):
    for raw in raw_items:
        raw_metadata = extract_metadata(raw)
        raw = raw['data']

        splited_items = split(raw, raw_metadata)
        for si in splited_items:
            si = datemize(si)
            si = identitize(si)
            si = modelize(si)
            item = metadata(raw_metadata, si)
            yield item


def extract_metadata(raw_item):
    raw_metadata = {
        'raw_uuid': raw_item['uuid'],
        'perceval_updated_on_ts': raw_item['updated_on'],
        'subtype': raw_item['backend_name'],
        'origin': raw_item['origin'],
        'tag': raw_item['tag'],
        'backend_version': raw_item['backend_version'],
        'retrieval_ts': raw_item['timestamp'],
        'arthur_job_id': None
    }
    return raw_metadata


def split(raw_item, raw_metadata):
    files = raw_item.pop('files')

    uuid_metadata = {
        'raw_uuid': raw_metadata['raw_uuid']
    }

    commit_uuid = generate_uuid(raw_item, uuid_metadata, 'commit')
    raw_item['item_uuid'] = commit_uuid
    raw_item['parent_uuid'] = None

    raw_item['added_lines'] =
    raw_item['removed_lines'] =
    raw_item['changed_lines'] =


    yield ('commit', raw_item)

    for file in files:
        uuid_metadata['parent_uuid'] = commit_uuid
        commit_action_uuid = generate_uuid(file, uuid_metadata, 'commit_action')
        file['item_uuid'] = commit_action_uuid
        file['parent_uuid'] = commit_uuid
        yield ('commit_action', file)

def datemize(item):
    if item[0] == "commit":
        return ("commit", datemize_commit(item[1]))
    elif item[0] == "commit_action":
        return item
    else:
        raise TypeError("Invalid type %s", item[0])


def datemize_commit(item):
    author_date = str_to_datetime(item['AuthorDate'])
    commit_date = str_to_datetime(item['CommitDate'])

    # TODO: extract in a better way this
    author_date_processed = {
        'date': author_date.timestamp(),
        'tz': author_date.tzinfo
    }

    commmit_date_processed = {
        'date': commit_date.timestamp(),
        'tz': commit_date.tzinfo
    }

    item['AuthorDate'] = author_date_processed
    item['CommitDate'] = commmit_date_processed

    return item


def identitize(item):
    if item[0] == "commit":
        return ("commit", identitize_commit(item[1]))
    elif item[0] == "commit_action":
        return item
    else:
        raise TypeError("Invalid type %s", item[0])


def identitize_commit(item):
    author = parse_identity(item['Author'])
    committer = parse_identity(item['Commit'])
    item['Author'] = author
    item['Commit'] = committer
    return item


def modelize(item):
    cs_item = CornerStoneItem()
    cs_item.data = item[1]
    return (item[0], cs_item)


def metadata(raw_metadata, cs):
    item_metadata = CornerStoneMetadata()
    cs_type = cs[0]
    cs_item = cs[1]
    for k, v in raw_metadata.items():
        setattr(item_metadata, k, v)

    item_metadata.uuid = cs_item.data.pop('item_uuid')
    item_metadata.parent_uuid = cs_item.data.pop('parent_uuid')
    item_metadata.model_version = '0.1.0'
    item_metadata.type = cs_type
    item_metadata.processed_ts = datetime_utcnow()

    cs_item.metadata = item_metadata

    return cs_item

def parse_identity(field):
    # John Smith <john.smith@bitergia.com>
    identity = {}

    git_user = field  # by default a specific user dict is expected

    fields = git_user.split("<")
    name = fields[0]
    name = name.strip() # Remove space between user and email
    email = None
    if len(fields) > 1:
        email = git_user.split("<")[1][:-1]
    identity['username'] = None
    identity['email'] = email
    identity['name'] = name if name else None

    return identity
