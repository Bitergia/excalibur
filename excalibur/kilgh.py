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
from perceval.backends.core.git import Git

from excalibur.data.furnace.element import Commit, CommitAction
from excalibur.builders.git_builders import CommitBuilder, FileActionBuilder
from excalibur.processors.git_processors import GitProcessor


def find_builder(element):

    if element.metadata.type == Commit.__name__ and \
            element.metadata.subtype == Git.__qualname__:
        builder = CommitBuilder(element)

    elif element.metadata.type == CommitAction.__name__ and \
            element.metadata.subtype == Git.__qualname__:
        builder = FileActionBuilder(element)

    else:
        raise NotImplementedError("Builder not found")

    return builder


class Kilgh:

    def __init__(self):
        self.processors = {}
        self.mock_db = {}
        self.ignored = 0

    def find_processor(self, element):
        """Return processor for a given element."""

        subtype = element.metadata.subtype
        if subtype in self.processors:
            processor = self.processors[subtype]

        elif subtype == Git.__qualname__:
            processor = GitProcessor()
            self.processors[subtype] = processor

        else:
            raise NotImplementedError("Processor not found")

        return processor

    def refine(self, elements):

        for element in elements:

            try:
                processor = self.find_processor(element)
                builder = find_builder(element)

                refined_item = builder.process()
                processor.add_item(refined_item)

                if processor.is_valid(refined_item):
                    for out_item in processor.items(refined_item):
                        self.mock_db[out_item.metadata.uuid] = out_item
                        yield out_item

                    # TODO remove refined items from processor as they were already processed and persisted

            except NotImplementedError as e:
                print("Ignoring element. Type:", element.metadata.type, "Subtype:", element.metadata.subtype,
                      "Reason:", str(e))
                self.ignored = self.ignored + 1
