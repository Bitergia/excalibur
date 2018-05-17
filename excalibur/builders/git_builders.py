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
import re

from perceval.backends.core.git import Git

from excalibur.data.furnace.element import Commit, CommitAction
from excalibur.data.spitfire.alloy import RefinedCommit, RefinedMetadata, IdentityData, RefinedFile
from excalibur.builders.builder import Builder


class CommitBuilder(Builder):

    def process(self):

        if self.element.metadata.type != Commit.__name__ or \
           self.element.metadata.subtype != Git.__qualname__:
            raise TypeError("Unrecognized element type")

        commit = RefinedCommit()
        commit.metadata = self._process_metadata()
        commit.project = self.__process_project(self.element.metadata.origin)

        # Process commit itself
        # TODO added and removed lines should be stored in a more robust way to avoid
        #      hiding changes. Using constants for keys could be a flexible approach.
        commit.added_lines = self.element.data_ext['added_lines']
        commit.removed_lines = self.element.data_ext['removed_lines']
        commit.changed_lines = self.element.data_ext['changed_lines']
        # TODO same as above's TODO
        commit.author = self.__process_identity(self.element.data['author_data']['name'],
                                                self.element.data['author_data']['email'],
                                                self.element.data['author_data']['username'])
        commit.author_date = self.element.data['author_date']['date']
        commit.author_tz = self.element.data['author_date']['tz']
        # TODO same as above's TODO
        commit.committer = self.__process_identity(self.element.data['committer_data']['name'],
                                                   self.element.data['committer_data']['email'],
                                                   self.element.data['committer_data']['username'])
        commit.committer_date = self.element.data['commit_date']['date']
        commit.committer_tz = self.element.data['commit_date']['tz']

        # TODO: rename 'nfiles' to a better name
        commit.nfiles = self.element.data_ext['action_files']

        commit.hash = self.element.data['hash']
        commit.message = self.element.data['message']
        commit.is_merge = 'Merge' in self.element.data

        return commit

    def __process_identity(self, name, email, username):
        identity_data = IdentityData()
        identity_data.bot = False
        identity_data.id = None
        identity_data.name = name
        identity_data.org_name = self.UNKNOWN_VALUE
        identity_data.user_name = username
        identity_data.uuid = None
        identity_data.domain = self.UNKNOWN_VALUE
        identity_data.last_action_date = None
        identity_data.first_action_date = None

        return identity_data

    def __process_project(self, repo_name):
        return self.UNKNOWN_VALUE

class FileActionBuilder(Builder):

    def process(self):

        if self.element.metadata.type != CommitAction.__name__ or \
           self.element.metadata.subtype != Git.__qualname__:
            raise TypeError("Unrecognized element type")

        file = RefinedFile()

        # RefinedElement props
        file.metadata = self._process_metadata()

        filepath = self.element.data.get('file')


        if filepath:
            file.filepath = filepath

            file.added_lines = self.element.data.get('added')
            file.removed_lines = self.element.data.get('removed')

            # To get correct dir name:
            # *  Replace multiple consecutive slashes by just one
            file_dir_name = filepath.replace('/+', '/')
            file_dir_name = file_dir_name[:file_dir_name.rfind('/') + 1]
            file.file_dir_name = file_dir_name

            file.file_name = filepath[filepath.rfind('/') + 1:]
            if file.file_name.rfind('.') == -1:
                file.file_ext = ''
            else:
                file.file_ext = file.file_name[file.file_name.rfind('.') + 1:]

            file.fileaction = self.element.data.get('action')

            # Clean filepath for splitting path parts:
            # * Replace multiple consecutive slashes by just one
            # * Remove leading slash if any, to avoid str.split to add an empty
            #   string to the resulting list of slices
            # * Remove trailing slash if any, to avoid str.split to add an empty
            #   string to the resulting list of slices
            file_path_list = filepath.replace('/+', '/')
            file_path_list = file_path_list.replace('^/', '')
            file_path_list = file_path_list.replace('/$', '')
            file_path_list = file_path_list.split('/')
            file.file_path_list = file_path_list

            filetype = 'Other'
            reg = re.compile(r"\.c$|\.h$|\.cc$|\.cpp$|\.cxx$|\.c\+\+$|\.cp$|\.py$|\.js$|\.java$|\.rs$")
            if reg.search(file.file_name):
                filetype = 'Code'
            file.filetype = filetype

        return file
