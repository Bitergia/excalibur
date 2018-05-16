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

from excalibur.data.furnace.element import (Issue,
                                            IssueJournal,
                                            User)
from .hammer import Hammer


class RedmineIssueHammer(Hammer):

    def smash(self):
        issue = Issue()
        issue.data = Hammer.copy_data(self.raw_data)
        issue.uuid = self.raw_metadata['uuid']

        author = self.__parse_identity(self.raw_data['author_data'])
        author = User(**author)
        author.parent_uuid = issue.uuid
        author.uuid = Hammer.create_uuid(author.parent_uuid, author.digest())

        issue.data['author_data'] = author.data
        yield author

        if 'assigned_to_data' in self.raw_data:
            assignee = self.__parse_identity(self.raw_data['assigned_to_data'])
            assignee = User(**assignee)
            assignee.parent_uuid = issue.uuid
            assignee.uuid = Hammer.create_uuid(assignee.parent_uuid, assignee.digest())

            issue.data['assignee_data'] = assignee.data
            yield assignee

        yield issue

        journals_raw = self.raw_data['journals']
        for journal_raw in journals_raw:
            journal = IssueJournal()
            journal.data = Hammer.copy_data(journal_raw)
            journal.parent_uuid = issue.uuid
            journal.uuid = Hammer.create_uuid(journal.parent_uuid,
                                              journal.data['id'])
            actor = self.__parse_identity(journal_raw['user_data'])
            actor = User(**actor)
            actor.parent_uuid = journal.uuid
            actor.uuid = Hammer.create_uuid(actor.parent_uuid, author.digest())

            journal.data['user_data'] = actor.data

            yield journal
            yield actor

    def datemize(self, element):
        if isinstance(element, User):
            return element

        created_on = element.data['created_on']
        element.data['created_on'] = str_to_datetime(created_on)

        if isinstance(element, Issue):
            updated_on = element.data['updated_on']
            element.data['updated_on'] = str_to_datetime(updated_on)
        return element

    def unify(self, element):
        if isinstance(element, User):
            return element

        element.data['created_at'] = element.data.pop('created_on')

        if isinstance(element, Issue):
            element.data.pop('author')
            element.data.pop('journals')
            element.data.pop('assigned_to', None)
            element.data.pop('assigned_to_data', None)
            element.data['title'] = element.data.pop('subject')
            element.data['body'] = element.data.pop('description')
            element.data['updated_at'] = element.data.pop('updated_on')
            return element
        elif isinstance(element, IssueJournal):
            element.data.pop('user')
            return element
        else:
            return element

    def __parse_identity(self, data):
        identity = {}
        identity['email'] = data["mail"] if "mail" in data else None
        identity['username'] = data["login"] if "login" in data else None
        identity['name'] = data["firstname"] + " " + data["lastname"] \
            if "firstname" in data and "lastname" in data else None

        return identity
