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

from copy import deepcopy
import json
import logging


from perceval.backends.core.git import (Git, CATEGORY_COMMIT)
from perceval.backends.core.github import (GitHub,
                                           CATEGORY_ISSUE as github_cat)
from perceval.backends.core.redmine import (Redmine,
                                            CATEGORY_ISSUE as redmine_cat)

from excalibur.errors import TomError
from excalibur.hammers.git_commit import GitCommitHammer
from excalibur.hammers.github_issue import GitHubIssueHammer
from excalibur.hammers.redmine_issue import RedmineIssueHammer


def find_hammer(raw_data, raw_metadata):
    if raw_metadata['category'] == CATEGORY_COMMIT and raw_metadata['backend_name'] == Git.__qualname__:
        hammer = GitCommitHammer(raw_data, raw_metadata)
    elif raw_metadata['category'] == github_cat and raw_metadata['backend_name'] == GitHub.__qualname__:
        hammer = GitHubIssueHammer(raw_data, raw_metadata)
    elif raw_metadata['category'] == redmine_cat and raw_metadata['backend_name'] == Redmine.__qualname__:
        hammer = RedmineIssueHammer(raw_data, raw_metadata)
    else:
        raise NotImplementedError("Hammer not found")

    return hammer


logger = logging.getLogger(__name__)


class Tom:

    def process(self, raw_items):
        for raw in raw_items:
            num_elements = 0
            raw_data = raw.pop('data')
            raw_metadata = raw

            hammer = find_hammer(raw_data, raw_metadata)
            elements = hammer.smash()
            for elem in elements:
                elem = hammer.datemize(elem)
                elem = hammer.modelize(elem)
                elem = hammer.unify(elem)
                elem = hammer.metadata(elem)
                elem = hammer.verify(elem)
                num_elements += 1
                yield elem

            if hammer.num_elements != num_elements:
                failed_raw = deepcopy(raw)
                failed_raw['data'] = raw_data
                msg = "Lost elements, %s/%s generated. Raw item %s" % (num_elements,
                                                                       hammer.num_elements,
                                                                       json.dumps(failed_raw,
                                                                                  sort_keys=True,
                                                                                  indent=4))
                raise TomError(msg=msg)
