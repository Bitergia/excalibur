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
from excalibur.data.spitfire.alloy import RefinedCommit, RefinedFile


class GitProcessor:

    def __init__(self):
        self.commits = {}
        self.files = {}

    def add_item(self, item):
        if type(item).__name__ == RefinedCommit.__name__:
            self.commits[item.metadata.uuid] = item

        elif type(item).__name__ == RefinedFile.__name__:

            if item.metadata.parent_uuid in self.files:
                self.files[item.metadata.parent_uuid].append(item)
            else:
                self.files[item.metadata.parent_uuid] = [item]

    def is_valid(self, item):
        """A commit or file is considered 'valid' iif all its elements, commit and files, if any,
        have been built and stored"""

        uuid = self.__common_uuid(item)

        valid = False
        if uuid in self.commits:
            commit = self.commits[uuid]
            if commit.nfiles == 0 or (self.files.get(uuid) and commit.nfiles == len(self.files[uuid])):
                valid = True

        return valid

    def items(self, item):
        """Return all stored items related to the same commit as the given item'"""
        uuid = self.__common_uuid(item)
        items = []

        if uuid in self.commits:
            items.append(self.commits[uuid])

        if uuid in self.files:
            items.extend(self.files[uuid])

        return items

    def remove_items(self, items):
        raise NotImplementedError


    def __common_uuid(self, item):

        if type(item).__name__ == RefinedCommit.__name__:
            uuid = item.metadata.uuid

        elif type(item).__name__ == RefinedFile.__name__:
            uuid = item.metadata.parent_uuid
        else:
            raise ValueError("Unrecognized type " + type(item).__name__)

        return uuid
