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

from perceval.backends.core.git import CATEGORY_COMMIT

from excalibur.hammers.git_commit import GitCommitHammer


from perceval.backends.core.git import (Git, CATEGORY_COMMIT)
from perceval.backends.core.github import (GitHub, CATEGORY_ISSUE)

from excalibur.hammers.git_commit import GitCommitHammer
from excalibur.hammers.github_issue import GitHubIssueHammer


def find_hammer(raw_data, raw_metadata):
    if raw_metadata['category'] == CATEGORY_COMMIT and raw_metadata['backend_name'] == Git.__qualname__:
        hammer = GitCommitHammer(raw_data, raw_metadata)
    elif raw_metadata['category'] == CATEGORY_ISSUE and raw_metadata['backend_name'] == GitHub.__qualname__:
        hammer = GitHubIssueHammer(raw_data, raw_metadata)
    else:
        raise NotImplementedError("Hammer not found")

    return hammer


class Tom:

    def process(self, raw_items):
        for raw in raw_items:
            raw_data = raw.pop('data')
            raw_metadata = raw

            hammer = find_hammer(raw_data, raw_metadata)
            elements = hammer.smash()
            for elem in elements:
                elem = hammer.datemize(elem)
                # elem = hammer.identitize(elem)
                elem = hammer.modelize(elem)
                elem = hammer.metadata(elem)
                yield elem
