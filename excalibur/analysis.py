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

class Node:
    def __init__(self):
        self.model_version = None
        self.uuid = None
        self.parent_uuid = None
        self.grimoire_creation_date = None
        self.subtype = None
        self.origin = None
        self.tag = None
        self.backend_version = None
        self.retrieval_ts = None
        self.processed_ts = None
        self.arthur_job_id = None
        self.raw_uuid = None
        self.origin = None

class Commit(Node):
    def __init__(self):
        self.added_lines = None
        self.removed_lines = None
        self.author = None
        self.author_date = None
        self.committer = None
        self.committer_date = None
        self.num_files = None
        self.commit_files = []
        self.hash = None
        self.message = None
        self.is_merge = None

class Project(Node):
    def __init__(self):
        self.project = None
        self.commits = []

class CommitFile(Node):
    def __init__(self):
        self.added_lines = None
        self.removed_lines = None
        self.num_files = None
        self.file_dir_name = None
        self.file_ext = None
        self.file_name = None
        self.file_path_list = None
        self.fileaction = None
        self.filepath = None
        self.filetype = None

class UniqueIdentity(None):
    def __init__(self):
        self.uuid = None
        self.identities = []
        self.author_max_date = None
        self.author_min_date = None

class Identity(Node):
    def __init__(self):
        self.bot = None
        self.id = None
        self.name = None
        self.org_name = None
        self.user_name = None
        self.uuid = None
        self.domain = None


def analysis(items):
    for item in items:
        if item.metadata.type == "commit":
            analyze_commit(item)
        elif item.metadata.type == "commit_action":
            analyze_commit_action(item)
        else:
            raise TypeError("Invalid type %s", item.metadata.type)


def analyze_commit(item):
    commit = create_commit(item)
    commit.author = give_me_sortinghat_identity(item.data['Author'])
    commit.committer = give_me_sortinghat_identity(item.data['Commit'])


def analyze_commit_action(item):
    pass

def give_me_sortinghat_identity(identity_data):
    identity = ask_sortinghat_for_identity(identity_data)
    save_identity(identity)
    return identity
