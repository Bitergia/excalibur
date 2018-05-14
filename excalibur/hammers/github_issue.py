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
                                            Issue,
                                            IssueComment,
                                            IssueReaction,
                                            User)
from .hammer import Hammer


class GitHubIssueHammer(Hammer):

    def smash(self):
        issue = Issue()
        issue.data = self.raw_data

        assignees = self.raw_data['assignees_data']
        assignees_lst = []
        for assignee in assignees:
            assignee_identity = self.__parse_identity(assignee)
            assignees_lst.append(assignee_identity)
            issue.data['assignees_identities'] = assignees_lst

        author = self.__parse_identity(self.raw_data['user_data'])
        issue.data['author_identity'] = author
        yield issue

        reactions_raw = self.raw_data['reactions_data']
        yield from self.__smash_reactions(reactions_raw, self.raw_metadata['uuid'])

        comments_raw = self.raw_data['comments_data']
        for comment_raw in comments_raw:
            comment = IssueComment()
            comment.data = comment_raw
            commenter_identity = self.__parse_identity(comment_raw['user_data'])
            comment.data['commenter_identity'] = commenter_identity
            yield comment

            reactions_raw = comment_raw["reactions_data"]
            yield from self.__smash_reactions(reactions_raw, comment.data['id'])

    def __smash_reactions(self, reactions_raw, parent_id):
        for reaction_raw in reactions_raw:
            reaction = IssueReaction()
            reaction.data = reaction_raw
            reaction.data_ext['parent_id'] = parent_id
            reactioner_identity = self.__parse_identity(reaction_raw['user_data'])
            reaction.data['reactioner_identity'] = reactioner_identity
            yield reaction

    def datemize(self, element):

        created_at = element.data['created_at']
        element.data['created_at'] = str_to_datetime(created_at)

        if not isinstance(element, IssueReaction):
            updated_at = element.data['updated_at']
            element.data['updated_at'] = str_to_datetime(updated_at)
        return element

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
        if isinstance(element, Issue):
            element.metadata.uuid = self.raw_metadata['uuid']
        elif isinstance(element, IssueComment):
            element.metadata.parent_uuid = self.raw_metadata['uuid']
            element.metadata.uuid = element.metadata.parent_uuid + str(element.data['id'])
        elif isinstance(element, IssueReaction):
            element.metadata.parent_uuid = element.data_ext.pop('parent_id')
            # FIXME: metadata parent_uuid is the comment id not a real uuid
            element.metadata.uuid = str(element.metadata.parent_uuid) + str(element.data['id'])
        else:
            raise TypeError("Invalid type %s", type(element))

        return element

    def __parse_identity(self, data):
        # John Smith <john.smith@bitergia.com>
        identity = {}

        email = data['email'] if 'email' in data else None
        name = data['name'] if 'name' in data else None
        username = data['login'] if 'login' in data else None

        identity['username'] = username
        identity['email'] = email
        identity['name'] = name if name else None

        return identity
