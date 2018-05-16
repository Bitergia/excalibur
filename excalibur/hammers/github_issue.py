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
                                            IssueComment,
                                            IssueReaction,
                                            User)
from .hammer import Hammer


class GitHubIssueHammer(Hammer):

    def smash(self):
        issue = Issue()
        issue.data = Hammer.copy_data(self.raw_data)
        issue.uuid = self.raw_metadata['uuid']

        author = self.__parse_identity(self.raw_data['user_data'])
        author = User(**author)
        author.parent_uuid = issue.uuid
        author.uuid = Hammer.create_uuid(author.parent_uuid, author.digest())

        issue.data['author_data'] = author.data
        yield author

        assignees_raw = self.raw_data['assignees_data']
        assignees = []
        for assignee_raw in assignees_raw:
            assignee = self.__parse_identity(assignee_raw)
            assignee = User(**assignee)
            assignee.parent_uuid = issue.uuid
            assignee.uuid = Hammer.create_uuid(assignee.parent_uuid, assignee.digest())
            assignees.append(assignee.data)
            yield assignee

        issue.data['assignees_data'] = assignees
        yield issue

        reactions_raw = self.raw_data['reactions_data']
        yield from self.__smash_reactions(reactions_raw, issue.uuid)

        comments_raw = self.raw_data['comments_data']
        for comment_raw in comments_raw:
            comment = IssueComment()
            comment.data = Hammer.copy_data(comment_raw)
            comment.parent_uuid = issue.uuid
            comment.uuid = Hammer.create_uuid(comment.parent_uuid,
                                              comment.data['id'])

            commenter = self.__parse_identity(comment_raw['user_data'])
            commenter = User(**commenter)
            commenter.parent_uuid = comment.uuid
            commenter.uuid = Hammer.create_uuid(commenter.parent_uuid, commenter.digest())

            comment.data['user_data'] = commenter.data

            yield comment
            yield commenter

            reactions_raw = comment_raw["reactions_data"]
            yield from self.__smash_reactions(reactions_raw, comment.uuid)

    def datemize(self, element):
        if isinstance(element, User):
            return element

        created_at = element.data['created_at']
        element.data['created_at'] = str_to_datetime(created_at)

        if not isinstance(element, IssueReaction):
            updated_at = element.data['updated_at']
            element.data['updated_at'] = str_to_datetime(updated_at)
        return element

    def unify(self, element):
        if isinstance(element, Issue):
            element.data.pop('assignee')
            element.data.pop('assignee_data')
            element.data.pop('assignees')
            element.data.pop('comments_data')
            element.data.pop('reactions_data')
            element.data.pop('user')
            element.data.pop('user_data')
            element.data.pop('comments_url')
            element.data.pop('events_url')
            element.data.pop('html_url')
            element.data.pop('labels_url')
            element.data.pop('repository_url')
            element.data.pop('pull_request')
            element.data_ext['labels'] = element.data.pop('labels')
            element.data_ext['reactions'] = element.data.pop('reactions')
            element.data_ext['url'] = element.data.pop('url')
            return element
        elif isinstance(element, IssueComment):
            element.data.pop('html_url')
            element.data.pop('issue_url')
            element.data.pop('reactions')
            element.data.pop('reactions_data')
            element.data.pop('user')
            element.data_ext['url'] = element.data.pop('url')
            return element
        elif isinstance(element, IssueReaction):
            element.data.pop('user')
            return element
        else:
            return element

    def __smash_reactions(self, reactions_raw, parent_uuid):
        for reaction_raw in reactions_raw:
            reaction = IssueReaction()
            reaction.data = Hammer.copy_data(reaction_raw)
            reaction.parent_uuid = parent_uuid
            reaction.uuid = Hammer.create_uuid(reaction.parent_uuid,
                                               reaction.data['id'])

            actor = self.__parse_identity(reaction_raw['user_data'])
            actor = User(**actor)
            actor.parent_uuid = reaction.uuid
            actor.uuid = Hammer.create_uuid(actor.parent_uuid, actor.digest())

            reaction.data['user_data'] = actor.data

            yield reaction
            yield actor

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
