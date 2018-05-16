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

from grimoirelab.toolkit.datetime import str_to_datetime

from excalibur.data.furnace.element import (CommitAction,
                                            Commit,
                                            User)
from .hammer import Hammer


class GitCommitHammer(Hammer):

    def smash(self):
        author_commit = self.__parse_identity(self.raw_data["Author"])
        committer_commit = self.__parse_identity(self.raw_data["Commit"])

        commit = Commit()
        commit.data = Hammer.copy_data(self.raw_data)
        commit.data['Author'] = author_commit
        commit.data['Commit'] = committer_commit
        commit.uuid = self.raw_metadata['uuid']

        author = User(**author_commit)
        author.parent_uuid = commit.uuid
        author.uuid = Hammer.create_uuid(author.parent_uuid, author.digest())
        committer = User(**committer_commit)
        committer.parent_uuid = commit.uuid
        committer.uuid = Hammer.create_uuid(committer.parent_uuid, committer.digest())

        commit.data['author_data'] = author.data
        commit.data['committer_data'] = committer.data

        yield commit
        yield committer
        yield author

        for action in self.raw_data['files']:
            commit_action = CommitAction()
            commit_action.data = Hammer.copy_data(action)
            commit_action.parent_uuid = self.raw_metadata['uuid']
            commit_action.uuid = Hammer.create_uuid(commit_action.parent_uuid,
                                                    commit_action.data['file'],
                                                    commit_action.data['action'])
            yield commit_action

    def datemize(self, element):
        if isinstance(element, Commit):
            return self.__datemize_commit(element)
        elif isinstance(element, CommitAction) or isinstance(element, User):
            return element
        else:
            raise TypeError("Invalid type %s", type(element))

    def modelize(self, element):
        if isinstance(element, Commit):
            action_files = self.raw_data['files']
            element.data_ext['added_lines'] = sum(
                [int(action['added']) for action in action_files if 'added' in action])
            element.data_ext['removed_lines'] = sum(
                [int(action['removed']) for action in action_files if 'removed' in action])
            element.data_ext['changed_lines'] = element.data_ext['added_lines'] + element.data_ext['removed_lines']
            element.data_ext['num_files'] = len(action_files)
            element.data_ext['is_merge'] = len(self.raw_data['parents']) > 1
            return element
        elif isinstance(element, CommitAction):
            element.data_ext['changed_lines'] = int(element.data['added']) + int(element.data['removed'])
            return element
        else:
            return element

    def unify(self, element):
        if isinstance(element, Commit):
            element.data.pop('files')
            element.data['author_date'] = element.data.pop('AuthorDate')
            element.data['commit_date'] = element.data.pop('CommitDate')
            element.data['hash'] = element.data.pop('commit')
            element.data.pop('Author')
            element.data.pop('Commit')
            return element
        elif isinstance(element, CommitAction):
            element.data['added_lines'] = element.data.pop('added')
            element.data['removed_lines'] = element.data.pop('removed')
            return element
        else:
            return element

    def __datemize_commit(self, element):
        data = element.data
        author_date = str_to_datetime(data['AuthorDate'])
        commit_date = str_to_datetime(data['CommitDate'])

        author_date_processed = {
            'date': author_date.timestamp(),
            'tz': author_date.tzinfo._offset.total_seconds()
        }

        commmit_date_processed = {
            'date': commit_date.timestamp(),
            'tz': commit_date.tzinfo._offset.total_seconds()
        }

        data['AuthorDate'] = author_date_processed
        data['CommitDate'] = commmit_date_processed

        return element

    @staticmethod
    def __parse_identity(field):
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
