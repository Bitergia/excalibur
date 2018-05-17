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
from elasticsearch import helpers

    # @classmethod
    # def process_commit_data(self, file, commit):
    #     """Add data coming from commit element to the given file"""
    #     if commit:
    #         file.author = commit.author
    #         file.project = commit.project
    #
    #         # RefinedFile props
    #         file.author_date = commit.author_date
    #         file.committer = commit.committer
    #         file.committer_date = commit.committer_date
    #
    #     return file
from excalibur.data.spitfire.alloy import RefinedCommit, RefinedFile
from excalibur.utils import epoch_to_millis


class ElasticWriter():

    def __init__(self, es_conn, es_index):
        self._es_conn = es_conn
        self._es_index = es_index

    def write_flat_item(self, flat_item):

        # Uploading info to the new ES
        doc = {
                "_index": self._es_index,
                "_type": "item",
                "_id": flat_item['uuid'],
                "_source": flat_item
        }

        # TODO exception and error handling
        return helpers.bulk(self._es_conn, [doc])


class GitCommitElasticWriter(ElasticWriter):

    def flatten(self, commit):
        """Flattens a given refined commit

        :param commit: a refined commit to be flattened
        """
        flat_commit = {}
        # Metadata
        flat_commit['uuid'] = commit.metadata.uuid
        flat_commit['parent_uuid'] = commit.metadata.parent_uuid
        flat_commit['raw_uuid'] = commit.metadata.raw_uuid
        flat_commit['perceval_updated_on_ts'] = epoch_to_millis(commit.metadata.perceval_updated_on_ts)
        flat_commit['model_version'] = commit.metadata.model_version
        flat_commit['type'] = commit.metadata.type
        flat_commit['subtype'] = commit.metadata.subtype
        flat_commit['origin'] = commit.metadata.origin
        flat_commit['tag'] = commit.metadata.tag
        flat_commit['backend_version'] = commit.metadata.backend_version
        flat_commit['retrieval_ts'] = epoch_to_millis(commit.metadata.retrieval_ts)
        flat_commit['processed_ts'] = epoch_to_millis(commit.metadata.processed_ts.timestamp())
        flat_commit['arthur_job_id'] = commit.metadata.arthur_job_id
        flat_commit['grimoire_creation_date'] = epoch_to_millis(commit.metadata.grimoire_creation_date)
        flat_commit['refinement_ts'] = epoch_to_millis(commit.metadata.refinement_ts.timestamp())

        # Identities
        flat_commit['author_bot'] = commit.author.bot
        flat_commit['author_id'] = commit.author.id
        flat_commit['author_name'] = commit.author.name
        flat_commit['author_org_name'] = commit.author.org_name
        flat_commit['author_user_name'] = commit.author.user_name
        flat_commit['author_uuid'] = commit.author.uuid
        flat_commit['author_domain'] = commit.author.domain
        flat_commit['author_date'] = epoch_to_millis(commit.author_date)
        # TODO extract timezone from dateutil.tz.tz.tzoffset
        flat_commit['author_tz'] = str(commit.author_tz)
        flat_commit['author_last_action_date'] = commit.author.last_action_date
        flat_commit['author_first_action_date'] = commit.author.first_action_date

        flat_commit['committer_bot'] = commit.committer.bot
        flat_commit['committer_id'] = commit.committer.id
        flat_commit['committer_name'] = commit.committer.name
        flat_commit['committer_org_name'] = commit.committer.org_name
        flat_commit['committer_user_name'] = commit.committer.user_name
        flat_commit['committer_uuid'] = commit.committer.uuid
        flat_commit['committer_domain'] = commit.committer.domain
        flat_commit['committer_date'] = epoch_to_millis(commit.committer_date)
        # TODO extract timezone from dateutil.tz.tz.tzoffset
        flat_commit['committer_tz'] = str(commit.committer_tz)
        flat_commit['committer_last_action_date'] = commit.committer.last_action_date
        flat_commit['committer_first_action_date'] = commit.committer.first_action_date
        # Project
        flat_commit['project'] = commit.project
        # Commit
        flat_commit['added_lines'] = commit.added_lines
        flat_commit['removed_lines'] = commit.removed_lines
        flat_commit['changed_lines'] = commit.changed_lines
        flat_commit['nfiles'] = commit.nfiles
        flat_commit['hash'] = commit.hash
        flat_commit['message'] = commit.message
        flat_commit['is_merge'] = commit.is_merge

        return flat_commit

    def write_item(self, refined_item):

        flat_item = self.flatten(refined_item)
        self.write_flat_item(flat_item)

class GitFileElasticWriter(ElasticWriter):

    def flatten(self, file, commit):
        """Flattens a given refined commit

        :param file: a refined file to be flattened
        :param commit: refined commit that included the file.
        """
        flat_file = {}
        # Metadata
        flat_file['uuid'] = file.metadata.uuid
        flat_file['parent_uuid'] = file.metadata.parent_uuid
        flat_file['raw_uuid'] = file.metadata.raw_uuid
        flat_file['perceval_updated_on_ts'] = epoch_to_millis(file.metadata.perceval_updated_on_ts)
        flat_file['model_version'] = file.metadata.model_version
        flat_file['type'] = file.metadata.type
        flat_file['subtype'] = file.metadata.subtype
        flat_file['origin'] = file.metadata.origin
        flat_file['tag'] = file.metadata.tag
        flat_file['backend_version'] = file.metadata.backend_version
        flat_file['retrieval_ts'] = epoch_to_millis(file.metadata.retrieval_ts)
        flat_file['processed_ts'] = epoch_to_millis(file.metadata.processed_ts.timestamp())
        flat_file['arthur_job_id'] = file.metadata.arthur_job_id
        flat_file['grimoire_creation_date'] = epoch_to_millis(file.metadata.grimoire_creation_date)
        flat_file['refinement_ts'] = epoch_to_millis(file.metadata.refinement_ts.timestamp())

        # Identities
        flat_file['author_bot'] = commit.author.bot
        flat_file['author_id'] = commit.author.id
        flat_file['author_name'] = commit.author.name
        flat_file['author_org_name'] = commit.author.org_name
        flat_file['author_user_name'] = commit.author.user_name
        flat_file['author_uuid'] = commit.author.uuid
        flat_file['author_domain'] = commit.author.domain
        flat_file['author_date'] = epoch_to_millis(commit.author_date)
        # TODO extract timezone from dateutil.tz.tz.tzoffset
        flat_file['author_tz'] = str(commit.author_tz)
        flat_file['author_last_action_date'] = commit.author.last_action_date
        flat_file['author_first_action_date'] = commit.author.first_action_date

        flat_file['committer_bot'] = commit.committer.bot
        flat_file['committer_id'] = commit.committer.id
        flat_file['committer_name'] = commit.committer.name
        flat_file['committer_org_name'] = commit.committer.org_name
        flat_file['committer_user_name'] = commit.committer.user_name
        flat_file['committer_uuid'] = commit.committer.uuid
        flat_file['committer_domain'] = commit.committer.domain
        flat_file['committer_date'] = epoch_to_millis(commit.committer_date)
        # TODO extract timezone from dateutil.tz.tz.tzoffset
        flat_file['committer_tz'] = str(commit.committer_tz)
        flat_file['committer_last_action_date'] = commit.committer.last_action_date
        flat_file['committer_first_action_date'] = commit.committer.first_action_date
        # Project
        flat_file['project'] = commit.project
        # Commit
        flat_file['nfiles'] = commit.nfiles
        flat_file['hash'] = commit.hash
        flat_file['message'] = commit.message
        flat_file['is_merge'] = commit.is_merge
        # File
        flat_file['added_lines'] = file.added_lines
        flat_file['removed_lines'] = file.removed_lines
        flat_file['file_dir_name'] = file.file_dir_name
        flat_file['file_ext'] = file.file_ext
        flat_file['file_name'] = file.file_name
        flat_file['file_path_list'] = file.file_path_list
        flat_file['fileaction'] = file.fileaction
        flat_file['filepath'] = file.filepath
        flat_file['filetype'] = file.filetype

        return flat_file

    def write(self, refined_file, refined_commit):

        flat_item = self.flatten(refined_file, refined_commit)
        self.write_flat_item(flat_item)
