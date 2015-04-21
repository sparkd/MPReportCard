#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import abc
import requests
from mp_data.tasks.base import BaseTask
from mp_data.lib.log import get_logger
import requests_cache

log = get_logger(__name__)


requests_cache.install_cache('_cache/data.parliament.bills')

class ParliamentTask(BaseTask):
    """
    Import early day motions from data.parliament.uk
    """

    url = 'http://lda.data.parliament.uk'

    results_per_page = 50

    # Default implementation
    params = {}

    @abc.abstractproperty
    def endpoint(self):
        pass

    @abc.abstractmethod
    def get_model_params(self, record):
        pass

    def run(self):


        self.params['_pageSize'] = self.results_per_page
        # self.params['familyName'] = 'Abrahams'

        self.params['_page'] = 1

        # We continue looping through until we don't get any more results
        while True:

            print 'Fetching page %s' % self.params['_page']

            response = requests.get(os.path.join(self.url, '%s.json' % self.endpoint), params=self.params)

            # Raise exception for any errors.
            response.raise_for_status()

            results = response.json()

            # No results - break out of loop
            if not results['result']['items']:
                break

            # Otherwise loop through results, creating new records
            for record in results['result']['items']:
                params = self.get_model_params(record)
                if params:
                    self.db_session.add(self.model(**params))

            self.db_session.commit()

            # Iterate page to get the next lot of results
            self.params['_page'] += 1

        print 'Committing records'
        self.db_session.commit()








