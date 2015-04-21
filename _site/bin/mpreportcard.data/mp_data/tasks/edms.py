#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
import csv
import luigi
from mp_data.tasks.base import BaseTask
from mp_data.tasks.file import FileTask
from mp_data.lib.log import get_logger
from mp_data.lib.helpers import list_missing_mp_names, get_twfy_ids
from mp_data.model import EDMSModel, MemberModel

log = get_logger(__name__)

class EDMSTask(BaseTask):

    """
    http://www.edms.org.uk/data/ has counts of EDMS signatures per session
    We'll just use these - but there is a better breakdown if required

    python tasks/edms.py --local-scheduler

    """

    session = luigi.Parameter(default=None)  # 12-13 - see available_sessions

    model = EDMSModel

    available_sessions = ['10-12', '12-13', '13-14', '14-15']

    def requires(self):

        # If a particular session is passed in, just build for that one
        # Otherwise use all sessions in available_sessions
        sessions = [self.session] if self.session else self.available_sessions

        for session in sessions:
            yield FileTask('http://www.edms.org.uk/data/mps_20%s.csv' % session)

    def run(self):

        missing_mp_names = list_missing_mp_names()

        # Create a list of pims ID so we can validate the member exists
        pims_ids = {m.pims_id: m.id for m in self.db_session.query(MemberModel).all()}
        twfy_ids = get_twfy_ids()

        for input in self.input():
            # We need the session - so extract from file
            session = re.search(r'(\d{2}\-\d{2})', input.path).group(1)

            log.info('Processing session %s', session)

            with input.open('r') as in_file:
                reader = csv.DictReader(in_file)
                for row in reader:

                    person_id = int(row['PersonID'])
                    edmi_id = int(row['EDMI ID'])

                    # PersonID = twfy_id
                    if person_id in twfy_ids:
                        member_id = twfy_ids[person_id]
                    # No matched twfy_id so try and match pims id
                    elif edmi_id in pims_ids:
                        member_id = pims_ids[edmi_id]
                    # Can't find an ID - but if this is a member we aren't interested in, continue
                    elif row['Name'] in missing_mp_names:
                        continue
                    elif person_id == 9006006:
                        # There is a type for this person ID (Mike Thornton)
                        # But we already have it so just continue
                        continue
                    else:
                        # Otherwise, raise an error for investigation
                        print row
                        raise Exception('Cannot retrieve member id for %s' % row['Name'])

                    self.db_session.add(self.model(
                        member_id=member_id,
                        number_of_signatures=row['No. of Signatures'],
                        session=session,
                        edms_id=person_id
                    ))

                    self.db_session.commit()

if __name__ == "__main__":
    luigi.run(main_task_cls=EDMSTask)