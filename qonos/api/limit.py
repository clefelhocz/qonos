# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Module borrowed from nova and simplified.

We are taking just the limit portion of the code at this point.

NOTE: As the rate-limiting here is done in memory, this only works per
process (each process will have its own rate limiting counter).
"""

import math
import re
import time

from qonos.openstack.common.gettextutils import _


class Limit(object):
    """Stores information about a limit for HTTP requests."""

    def __init__(self, verb, uri, regex, value, seconds):
        """Initialize a new `Limit`.

        @param verb: HTTP verb (POST, PUT, etc.)
        @param uri: Human-readable URI
        @param regex: Regular expression format for this limit
        @param value: Integer number of requests which can be made
        @param seconds: Time interval in seconds for number of requests
        """
        self.verb = verb
        self.uri = uri
        self.regex = regex
        self.value = int(value)
        self.unit = seconds
        self.remaining = int(value)

        if value <= 0:
            raise ValueError("Limit value must be > 0")

        self.last_request = None
        self.next_request = None

        self.water_level = 0
        self.capacity = self.unit
        self.request_value = float(self.capacity) / float(self.value)
        msg = _("Only %(value)s %(verb)s request(s) can be "
                "made to %(uri)s every %(unit)s seconds.")
        self.error_message = msg % self.__dict__

    def __call__(self, verb, url):
        """Represents a call to this limit from a relevant request.

        @param verb: string http verb (POST, GET, etc.)
        @param url: string URL
        """
        if self.verb != verb or not re.match(self.regex, url):
            return

        now = self._get_time()

        if self.last_request is None:
            self.last_request = now

        leak_value = now - self.last_request

        self.water_level -= leak_value
        self.water_level = max(self.water_level, 0)
        self.water_level += self.request_value

        difference = self.water_level - self.capacity

        self.last_request = now

        if difference > 0:
            self.water_level -= self.request_value
            self.next_request = now + difference
            return difference

        cap = self.capacity
        water = self.water_level
        val = self.value

        self.remaining = math.floor(((cap - water) / cap) * val)
        self.next_request = now

    def _get_time(self):
        """Retrieve the current time. Broken out for testability."""
        return time.time()

    def display(self):
        """Return a useful representation of this class."""
        return {
            "verb": self.verb,
            "URI": self.uri,
            "regex": self.regex,
            "value": self.value,
            "remaining": int(self.remaining),
            "unit": self.unit,
            "resetTime": int(self.next_request or self._get_time()),
        }
