#!/usr/bin/env python3
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

import pkg_resources
from elasticsearch import Elasticsearch
from kidash.kidash import feed_dashboard
from perceval.backends.core.git import Git

from excalibur.data.furnace.element import Commit, CommitAction
from excalibur.writers.git_writers import GitCommitElasticWriter, GitFileElasticWriter

ES_URL = 'http://localhost:9200'


GIT_ALIAS = 'git'
GIT_AREAS_OF_CODE_ALIAS = 'git_areas_of_code'

class Velazquez():

    def __init__(self, mock_db):

        # TODO connections should depend on writing config
        # Creating connections
        self.commit_out_index = 'git_excalibur'
        self.file_out_index = 'git_excalibur_aoc'
        self.es_conn = Elasticsearch([ES_URL], timeout=100)

        self.mock_db = mock_db

    def paint(self):

        print("[Velázquez] Starting my paintings...")

        self.init_es_index(self.commit_out_index, 'mappings/git.json')
        self.init_es_index(self.file_out_index, 'mappings/git_aoc.json')

        eswriter_commit = GitCommitElasticWriter(self.es_conn, self.commit_out_index)
        eswriter_file = GitFileElasticWriter(self.es_conn, self.file_out_index)

        for refined_item in self.mock_db.values():
            # TODO writers should be activated depending on config
            if refined_item.metadata.type == Commit.__name__ and \
                    refined_item.metadata.subtype == Git.__qualname__:
                eswriter_commit.write_item(refined_item)

            elif refined_item.metadata.type == CommitAction.__name__ and \
                    refined_item.metadata.subtype == Git.__qualname__:
                refined_commit = self.mock_db.get(refined_item.metadata.parent_uuid)
                eswriter_file.write(refined_item, refined_commit)

            else:
                print("[Velázquez] Don't know how to paint that", refined_item.metadata.subtype,
                      refined_item.metadata.type)

        # Create aliases
        self.create_alias(self.commit_out_index, GIT_ALIAS)
        self.create_alias(self.file_out_index, GIT_AREAS_OF_CODE_ALIAS)

        # Load panel
        self.load_panel('panels/git_panel.json')
        self.load_panel('panels/git_areas_of_code.json')

        print("[Velázquez] Exhibition ready for visitors")


    def init_es_index(self, index_name, mapping_path):
        exists_index = self.es_conn.indices.exists(index=index_name)
        # TODO support incremental mode instead of deleting index by default
        if exists_index:
            # Initialize out index
            self.es_conn.indices.delete(index_name, ignore=[400, 404])
        # TODO put mapping
        mappings_file = pkg_resources.resource_filename('excalibur', mapping_path)
        # Read Mapping
        with open(mappings_file) as f:
            mapping = f.read()
        self.es_conn.indices.create(index_name, body=mapping)

    def create_alias(self, index_name, alias_name):
        exists_index = self.es_conn.indices.exists(index=index_name)
        if exists_index:
            if not self.es_conn.indices.exists_alias(name=alias_name):
                print("[Velázquez] Creating alias:", alias_name)
                self.es_conn.indices.put_alias(index=index_name, name=alias_name)
            else:
                print("[Velázquez] Alias", alias_name, "already exists")
        else:
            print("[Velázquez] Cannot create alias", alias_name,": index", index_name, "does not exist")

    def load_panel(self, panel_path):
        print("[Velázquez] Painting panel from", panel_path)

        panel_file = pkg_resources.resource_filename('excalibur', panel_path)
        # Read Mapping
        with open(panel_file) as f:
            dashboard = json.load(f)

        feed_dashboard(dashboard, ES_URL)
        print("[Velázquez] Painting ready for", panel_path)