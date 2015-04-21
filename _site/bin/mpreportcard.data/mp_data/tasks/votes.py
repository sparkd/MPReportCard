#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import urllib
import re
import luigi
import urlparse
from datetime import datetime, date
from sqlalchemy import func
from mp_data import ELECTION_DATE, MP_COUNT
from mp_data.lib.log import get_logger
from mp_data.tasks.base import BaseTask
from mp_data.tasks.public_whip_ids import PublicWhipIDTask
from mp_data.lib.helpers import get_soup
from mp_data.model import VotesModel, MembersVotesModel, MemberModel, PublicWhipIDModel

log = get_logger(__name__)

class VotesTask(BaseTask):

    """
    Retrieving voting information from Public Whip
    """

    model = VotesModel

    def run(self):

        # The MP page with display=everyvote parameter lists every vote
        # We're just using DA as she's top of the list and has been in parliament since 2010
        url = 'http://www.publicwhip.org.uk/mp.php?mpn=Diane_Abbott&display=everyvote#divisions'

        for vote in self.parse_votes(url):

            # Only used for an individual member's votes
            for d in ['result', 'voted', 'role']:
                del vote[d]

            # Create a new model
            self.db_session.add(self.model(**vote))

        self.db_session.commit()

    @staticmethod
    def parse_votes(url):
        """
        Parse the page soup, extracting all the votes from the html table
        """

        soup = get_soup(url, 'votes.soup')

        # Get all rows from the table
        rows = soup.find("table", {"class": "votes"}).findChildren('tr', {"class": ["odd", "even"]})

        # Loop through each row
        for row in rows:

            params = {}

            tds = row.findAll("td")

            # John Bercow has no votes - check for this and continue
            # There will be one td with colspan
            if tds[0].text == 'no votes listed':
                continue

            # The second cell contains the date string
            date_str = tds[1].text.encode('utf-8')

            params['date'] = datetime.strptime(date_str, '%d\xc2\xa0%b\xc2\xa0%Y').date()

            # Stop processing once we get past the date of the last election
            if params['date'] < ELECTION_DATE:
                break

            # Third cell contains link to the vote page
            a = tds[2].find('a')
            # Parse the HREF to extract the vote number
            parsed_url = urlparse.urlparse(a["href"])
            query = urlparse.parse_qs(parsed_url.query)

            params['title'] = a.text
            # Add vote session id - this is unique vote identifier per session
            # So they are duplicated for each year 20-11, 11-12 etc.,
            params['session_id'] = int(query['number'][0])

            # Loop through the extra fields and their position in the table
            for col, key in [(3, 'result'), (4, 'voted'), (5, 'role')]:
                params[key] = tds[col].text.lower().strip()

            yield params


class MemberVotesTask(VotesTask):

    """
    Parse an MP voting page on Public Whip and link votes to the VotesModel
    """

    model = MembersVotesModel

    # Get interests for a particular MP - Member ID
    mpid = luigi.Parameter(default=None)

    def requires(self):
        # Before this can run we want to have imported all of the public whip IDs
        yield PublicWhipIDTask(), VotesTask()

    def run(self):

        votes_dict = self.get_votes()

        # Loop through all MPs via their public whip ID
        for mp in self.db_session.query(PublicWhipIDModel).all():

            if self.mpid and mp.member_id != int(self.mpid):
                continue

            log.info('%s: Retrieving votes', mp.pw_id)

            url = 'http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip%2Fmember%2F{mp}&house=commons&display=allvotes'.format(
                mp= mp.pw_id
            )

            for vote in self.parse_votes(url):

                # The date of the vote
                date = vote.pop('date')

                # The vote id (unique per session)
                session_id = vote.pop('session_id')

                # # Get the vote ID from our database - the vote session id is only unique per session
                # # So lookup our internal DB primary key via session and date
                vote['vote_id'] = votes_dict[(session_id, date)]

                vote['member_id'] = mp.member_id

                # Only used for the vote itself
                del vote['title']

                self.db_session.add(self.model(**vote))

            # try:
            self.db_session.commit()
            # except Exception:
            #     self.db_session.rollback()
            #     print " -- ERROR -- "

    def get_votes(self):
        """
        Get dictionary of vote IDs, keyed by (date, pwid)
        @return:
        """
        votes = {}

        for vote in self.db_session.query(VotesModel).all():
            votes[(vote.session_id, vote.date)] = vote.id

        return votes

if __name__ == "__main__":
    luigi.run(main_task_cls=MemberVotesTask)