#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import sys
import luigi
import requests
import untangle
from mp_data.model import WriteToThemModel
from mp_data.tasks.base import BaseTask
from mp_data.lib.log import get_logger
from mp_data.lib.helpers import get_number_from_string, get_pw_ids, get_twfy_ids

log = get_logger(__name__)


class WriteToThemTask(BaseTask):

    """

    Parse data from writetothem.com
    https://www.writetothem.com/stats/2013/mps?xml=1

    python tasks/answers.py --local-scheduler

    optional param: year

    """

    model = WriteToThemModel

    year = luigi.Parameter(default='2013')

    def run(self):

        twfy_ids = get_twfy_ids()
        url = os.path.join('https://www.writetothem.com/stats', self.year, 'mps?xml=1')
        doc = untangle.parse(url)

        for person in doc.writetothem.personinfo:

            # The ID is in the format uk.org.publicwhip/person/24809
            # However, the numeric ID seems to be a theyworkforyou ID, not
            # a public whip ID
            id = get_number_from_string(person['id'])

            # print pwid
            # Get the member ID

            try:
                member_id = twfy_ids[id]
            except KeyError:

                # If it's not one of our known missing MPs (resigned etc.,)
                # Raise an exception
                if id not in [10170, 11109, 10232, 11113, 11565, 10387]:
                    raise Exception("Missing ID %s" % id)

            else:

                data = {
                    'member_id': member_id,
                    'year': self.year,
                    'total_sent': person['writetothem_sent_%s' % self.year],
                    'surveys': person['writetothem_responsiveness_responded_outof_%s' % self.year],
                    'replies': person['writetothem_responsiveness_responded_%s' % self.year],
                    'data_quality_indicator': person['writetothem_responsiveness_data_quality_category_%s' % self.year]
                }

                self.db_session.add(self.model(**data))

            self.db_session.commit()


if __name__ == "__main__":
    luigi.run(main_task_cls=WriteToThemTask)