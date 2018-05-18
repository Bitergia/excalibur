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

import configparser
import logging

from sortinghat import api
from sortinghat import utils
from sortinghat.db.database import Database
from sortinghat.exceptions import AlreadyExistsError, WrappedValueError

from excalibur.data.furnace.element import User
from excalibur.errors import TongsError


logger = logging.getLogger(__name__)


SH_CONFIG_FILE = '../sortinghat.conf'


class Tongs:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(SH_CONFIG_FILE)
        self.db_kwargs = {'user': config['Database']['user'],
                          'password': config['Database']['password'],
                          'database': config['Database']['name'],
                          'host': config['Database']['host'],
                          'port': config['Database']['port']}
        self.db = Database(**self.db_kwargs)

    def process(self, elements):
        no_identities = []
        num_identites = 0
        num_no_identities = 0
        for elem in elements:

            if isinstance(elem, User):
                self.__add_identity(elem)
                num_identites += 1
            else:
                no_identities.append(elem)
                num_no_identities += 1
                yield elem

        if len(elements) != (num_identites + num_no_identities):
            msg = "Lost elements, total elements %s, identities %s, others %s" % (len(elements),
                                                                                  num_identites,
                                                                                  num_no_identities)
            raise TongsError(cause=msg)

    def __add_identity(self, elem):
        email = elem.data['email']
        name = elem.data['name']
        username = elem.data['username']
        source = elem.metadata.subtype
        try:
            uuid = api.add_identity(self.db, source, email, name, username)

            profile = {"name": name if name else username,
                       "email": email}

            api.edit_profile(self.db, uuid, **profile)
        except AlreadyExistsError as ex:
            uuid = ex.uuid
        except WrappedValueError:
            logger.warning("Trying to add a None identity. Ignoring it. uuid: %s, parent_uuid: %s",
                           elem.uuid, elem.parent_uuid)
        except UnicodeEncodeError:
            logger.warning("UnicodeEncodeError. Ignoring it. %s %s %s. uuid: %s, parent_uuid: %s",
                           elem.data['email'], elem.data['name'], elem.data['username'],
                           elem.uuid, elem.parent_uuid)
        except Exception as ex:
            logger.warning("Unknown exception adding identity. Ignoring it. %s %s %s. uuid: %s, parent_uuid: %s",
                           elem.data['email'], elem.data['name'], elem.data['username'],
                           elem.uuid, elem.parent_uuid)
            raise TongsError(cause=str(ex))

        return uuid

    def retrieve_unique_identity(self, source, name, email, username):
        uuid = utils.uuid(source, email, name, username)
        unique_identity = api.unique_identities(self.db, uuid=uuid)[0]

        if not unique_identity.profile:
            msg = "No profile for uuid (name: %s, email: %s, username: %s" % (uuid, name, email, username)
            logger.error(msg)
            raise TongsError(cause=msg)

        return unique_identity
