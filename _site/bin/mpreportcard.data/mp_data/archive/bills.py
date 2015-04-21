#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""
import re
import luigi
from mp_data.model import EDMSBill, Member
from mp_data.tasks.parliament import ParliamentTask
from mp_data.lib.log import get_logger

log = get_logger(__name__)


class EDMSBillTask(ParliamentTask):
    """
    Import early day motions from data.parliament.uk
    """

    endpoint = 'edms'

    model = EDMSBill

    params = {
        '_view': 'all',
        'min-dateTabled': '2010-05-06'
    }

    def get_model_params(self, record):

        sponsor_members = []

        try:
            sponsors = self.ensure_list(record['sponsor'])
        except KeyError:
            pass
        else:

            # Make sure we have the primary sponsor included
            if record['primarySponsor'] != record['creator'] and record['primarySponsor'] not in sponsors:
                sponsors += self.ensure_list(record['primarySponsor'])

            sponsor_members = self.get_members(sponsors)

        # In the very rare occasion that we have multiple creators
        if isinstance(record['creator'], list):
            # Add the extra creators to the sponsor list
            sponsor_members += self.get_members(record['creator'][1:])
            record['creator'] = record['creator'][0]

        creator_id = self.uri_get_id(record['creator'])

        if creator_id in self.members:
            return {
                'title': record['title'],
                'date': record['dateTabled']['_value'],
                'creator': creator_id,
                'sponsors': sponsor_members
            }
        else:
            print 'Missing creator %s' % creator_id

if __name__ == "__main__":
    luigi.run(main_task_cls=EDMSBillTask)





