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
import json

from excalibur.data.furnace.element import ElementMetadata, json_date_handler


class RefinedMetadata(ElementMetadata):

    def __init__(self):

        super().__init__()

        self.grimoire_creation_date = None
        self.refinement_ts = None


class IdentityData():

    def __init__(self):
        self.bot = None
        self.id = None
        self.name = None
        self.org_name = None
        self.user_name = None
        self.uuid = None
        self.domain = None
        self.last_action_date = None # author_max_date
        self.first_action_date = None # author_min_date

    def __str__(self):
        return str(self.__dict__)


class RefinedElement():

    def __init__(self):
        self.metadata = None

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4,
                          default=json_date_handler)


class RefinedProjectElement(RefinedElement):

    def __init__(self):
        super().__init__()
        self.project = None


class RefinedCommit(RefinedProjectElement):

    def __init__(self):

        super().__init__()

        self.added_lines = None
        self.removed_lines = None
        self.changed_lines = None
        self.author = None
        self.author_date = None
        self.author_tz = None
        self.committer = None
        self.committer_date = None
        self.committer_tz = None
        self.nfiles = None
        self.hash = None
        self.message = None
        self.is_merge = None


class RefinedFile(RefinedElement):

    def __init__(self):

        super().__init__()

        self.added_lines = None
        self.removed_lines = None
        self.file_dir_name = None
        self.file_ext = None
        self.file_name = None
        self.file_path_list = None
        self.fileaction = None
        self.filepath = None
        self.filetype = None