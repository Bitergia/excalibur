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

from grimoirelab.toolkit.datetime import (datetime_utcnow,
                                          str_to_datetime)

from excalibur.data.furnace.element import (ElementMetadata,
                                            CommitAction,
                                            Commit)
from .hammer import Hammer


class GitCommitHammer(Hammer):

    def smash(self):
        action_files = self.raw_data.pop('files')

        commit = Commit()
        commit.data = self.raw_data
        commit.data_ext['added_lines'] = sum([int(action['added']) for action in action_files if 'added' in action])
        commit.data_ext['removed_lines'] = sum([int(action['removed']) for action in action_files if 'removed' in action])
        commit.data_ext['changed_lines'] = commit.data_ext['added_lines'] + commit.data_ext['removed_lines']
        commit.data_ext['num_files'] = len(action_files)

        yield commit

        for action in action_files:
            commit_action = CommitAction()
            commit_action.data = action
            yield commit_action

    def datemize(self, element):
        if isinstance(element, Commit):
            return self.__datemize_commit(element)
        elif isinstance(element, CommitAction):
            return element
        else:
            raise TypeError("Invalid type %s", type(element))

    def identitize(self, element):
        if isinstance(element, Commit):
            return self.__identitize_commit(element)
        elif isinstance(element, CommitAction):
            return element
        else:
            raise TypeError("Invalid type %s", type(element))

    def modelize(self, element):
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

        element = self.uuid(element)

        return element

    def uuid(self, element):
        if isinstance(element, Commit):
            element.metadata.uuid = self.raw_metadata['uuid']
        elif isinstance(element, CommitAction):
            element.metadata.parent_uuid = self.raw_metadata['uuid']
            element.metadata.uuid = element.metadata.parent_uuid + element.data['file']
        else:
            raise TypeError("Invalid type %s", type(element))

        return element

    def __datemize_commit(self, element):
        data = element.data
        author_date = str_to_datetime(data['AuthorDate'])
        commit_date = str_to_datetime(data['CommitDate'])

        # TODO: extract in a better way this
        author_date_processed = {
            'date': author_date.timestamp(),
            'tz': author_date.tzinfo
        }

        commmit_date_processed = {
            'date': commit_date.timestamp(),
            'tz': commit_date.tzinfo
        }

        data['AuthorDate'] = author_date_processed
        data['CommitDate'] = commmit_date_processed

        return element

    def __identitize_commit(self, element):
        data = element.data
        author = self.__parse_identity(data['Author'])
        committer = self.__parse_identity(data['Commit'])
        data['Author'] = author
        data['Commit'] = committer

        return element

    def __parse_identity(self, field):
        # John Smith <john.smith@bitergia.com>
        identity = {}

        git_user = field  # by default a specific user dict is expected

        fields = git_user.split("<")
        name = fields[0]
        name = name.strip()  # Remove space between user and email
        email = None
        if len(fields) > 1:
            email = git_user.split("<")[1][:-1]

        identity['username'] = None
        identity['email'] = email
        identity['name'] = name if name else None

        return identity
