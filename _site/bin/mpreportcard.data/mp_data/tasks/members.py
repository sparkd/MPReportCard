#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import re
import luigi
import requests
import requests_cache
from mp_data.tasks.base import BaseTask
from mp_data.tasks.constituency import ConstituencyTask
from mp_data.lib.log import get_logger
from mp_data.model import MemberModel
from mp_data.lib.helpers import ensure_list, get_constituencies
from mp_data import ELECTION_DATE
from dateutil import parser

log = get_logger(__name__)

requests_cache.install_cache('_cache/data.parliament.members')

class MembersTask(BaseTask):

    """
    Get members from http://data.parliament.uk/membersdataplatform/memberquery.aspx#outputs

    python tasks/members.py --local-scheduler

    """

    model = MemberModel

    # Member id
    id = luigi.IntParameter(default=None)

    def requires(self):
        yield ConstituencyTask()

    def _request(self, buckets):

        url = ['http://data.parliament.uk/membersdataplatform/services/mnis/members/query']

        if self.id:
            url.append('id=%s' % self.id)

        url.append('house=commons')
        url.append(buckets)

        headers = {
            'content-type': 'application/json'
        }

        response = requests.get(os.path.join(*url), headers=headers)
        # The response has byte order mark, which causes json() to fail
        # Set the encoding fixes the issue - see http://stackoverflow.com/questions/24554458/how-to-remove-byte-order-mark-in-python
        response.encoding = "utf-8-sig"

        result = response.json()

        return result['Members']['Member']

    def get_members(self):

        return self._request('Addresses|Constituencies|Committees')

    def run(self):

        constituencies_dict = get_constituencies()

        for member in self.get_members():

            member_id = int(member['@Member_Id'])

            data = {
                'id': member_id,
                'pims_id': int(member['@Pims_Id']),
                'dods_id': int(member['@Dods_Id']),
                'gender': member['Gender'],
                'party': member['Party']['#text'],
                'start_date': member[u'CurrentStatus'][u'StartDate'],
                'date_of_birth': member[u'DateOfBirth'],
                'name': member[u'DisplayAs'],
                'list_name': member[u'ListAs']  # Remove if not used for joining with interests
            }

            # Wrong for David Laws
            if member_id == '1473':
                data['start_date'] = None;

            try:
                data['number_committees'] = len(member['Committees']['Committee'])
            except TypeError:
                data['number_committees'] = 0

            # Loop through each address
            for address in member['Addresses']['Address']:

                # Is it either the website or twitter
                for address_type in [u'Website', u'Twitter']:
                    if address['Type'] == address_type:
                        data[address_type.lower()] = address['Address1']

            for constituency in ensure_list(member['Constituencies']['Constituency']):

                dt = parser.parse(constituency[u'StartDate'])
                # If date is since the election data, add it
                if dt.date() >= ELECTION_DATE:
                    data['constituency_id'] = constituencies_dict[constituency['Name'].lower()]
                    if constituency['EndReason'] and 'Standing Down' in constituency['EndReason']:
                        data['standing_down'] = True
                    else:
                        data['standing_down'] = False
                    break

            self.db_session.add(self.model(**data))

        self.db_session.commit()


if __name__ == "__main__":
    luigi.run(main_task_cls=MembersTask)