#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
import os
import abc
import luigi
import requests
import requests_cache
from mp_data.tasks.base import BaseTask
from mp_data.lib.log import get_logger
from mp_data.model import MemberModel, CommonsWrittenQuestionModel, CommonsOralQuestionModel

log = get_logger(__name__)

requests_cache.install_cache('_cache/data.parliament.bills')

class CommonsQuestionsTask(BaseTask):
    """
    Import commons questions from data.parliament.uk

    python tasks/commons_questions.py  CommonsWrittenQuestionsTask --local-scheduler
    python tasks/commons_questions.py  CommonsOralQuestionsTask --local-scheduler

    """

    endpoint = 'http://lda.data.parliament.uk'

    results_per_page = 50

    params = {
        '_view': 'all',
        'min-dateTabled': '2010-05-06',
    }

    # MP ID
    id = luigi.Parameter(default=None)

    def __init__(self, *args, **kwargs):

        super(CommonsQuestionsTask, self).__init__(*args, **kwargs)

        # Pre-load all the members into a dictionary keyed by ID
        self.members = {m.id: m for m in self.db_session.query(MemberModel).all()}

        # Delete anything before running
        self.delete_entries()

    @abc.abstractproperty
    def path(self):
        """
        Add path to endpoint - matching http://lda.data.parliament.uk/
        @return:
        """
        pass

    @staticmethod
    def get_id_from_uri(uri):
        return int(re.search(r'(\d+)', uri).group(1))

    def get_members(self, uris):

        m = []

        for uri in uris:
            member_id = self.get_id_from_uri(uri)
            try:
                m.append(self.members[member_id])
            except KeyError:
                # Member does not exists - not a huge error as this
                # will be deceased and retired MPs
                log.debug('Member %s does not exist', member_id)

        return m

    def run(self):

        self.params['_pageSize'] = self.results_per_page

        # Passing in an ID causes a 500 server error
        # if self.id:
        #     self.params['creator'] = self.id

        self.params['_page'] = 1

        # We continue looping through until we don't get any more results
        while True:

            print 'Fetching page %s' % self.params['_page']

            response = requests.get(os.path.join(self.endpoint, '%s.json' % self.path), params=self.params)

            # Raise exception for any errors.
            response.raise_for_status()

            results = response.json()

            # No results - break out of loop
            if not results['result']['items']:
                break

            # Otherwise loop through results, creating new records
            for record in results['result']['items']:

                tabling_member_id = self.get_id_from_uri(record['tablingMember'])

                # If this tabling member is one of our current members, add it
                if tabling_member_id in self.members:
                    self.db_session.add(self.model(
                        date=record['dateTabled']['_value'],
                        tabling_member=tabling_member_id,
                        question_text=record['questionText'],
                        registered_interest=record['RegisteredInterest']['_value'],
                    ))
                else:
                    print 'Missing creator %s' % tabling_member_id

            self.db_session.commit()

            # Iterate page to get the next lot of results
            self.params['_page'] += 1

        print 'Committing records'
        self.db_session.commit()

class CommonsWrittenQuestionsTask(CommonsQuestionsTask):

    path = 'commonswrittenquestions'
    model = CommonsWrittenQuestionModel


class CommonsOralQuestionsTask(CommonsQuestionsTask):

    path = 'commonsoralquestions'
    model = CommonsOralQuestionModel


if __name__ == "__main__":
    luigi.run()