#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import abc
import luigi
import requests
import requests_cache
from pymongo import MongoClient
from mp_data.lib.log import get_logger
from mp_data import THEYWORKFORYOU_API_KEY
from mp_data import config

requests_cache.install_cache('_cache/theyworkforyou')

log = get_logger(__name__)

class TheyWorkForYouTask(luigi.Task):

    """
    They work for you has loads of info on MPs
    Loads this into mongo so we can analyse and extract the data we need
    """

    endpoint = 'http://www.theyworkforyou.com/api/'

    @abc.abstractproperty
    def path(self):
        """
        Add path to endpoint - matching http://lda.data.parliament.uk/
        @return:
        """
        pass

    @abc.abstractproperty
    def collection(self):
        """
        MongoDB collection
        """
        pass

    def get_collection(self):
        return self.mongo_db[self.collection]

    def __init__(self, *args, **kwargs):

        super(TheyWorkForYouTask, self).__init__(*args, **kwargs)
        client = MongoClient(config.get('mongo', 'host'))
        self.mongo_db = client[config.get('mongo', 'db')]

    def _call_api(self, **kwargs):
        """
        Helper function to call API
        @param params:
        @return:
        """

        # Add the API key
        kwargs['key'] = THEYWORKFORYOU_API_KEY
        response = requests.get(os.path.join(self.endpoint, self.path), params=kwargs)

        # Raise exception for any errors.
        response.raise_for_status()

        return response.json()

    def complete(self):
        """
        Is complete if we have records in the collection
        To run again, delete the collection
        :return:
        """
        if self.get_collection().find_one():
            return True

class TheyWorkForYouGetMPTask(TheyWorkForYouTask):

    path = 'getMPs'
    collection = 'mp_list'

    def run(self):

        results = self._call_api()

        # Remap using the person_id as primary key (_id)
        for mp in results:
            mp['_id'] = mp['person_id']
            del mp['person_id']

        self.get_collection().insert(results)

class TheyWorkForYouGetMPInfoTask(TheyWorkForYouTask):

    path = 'getMPsInfo'

    collection = 'mp_info'

    def requires(self):
        yield TheyWorkForYouGetMPTask()

    def get_mp_ids(self):
        """
        Retrieve list of IDs imported by TheyWorkForYouGetMPTask
        @return:
        """

        cursor = self.mongo_db[TheyWorkForYouGetMPTask.collection].find({}, {'_id': True})
        return [record['_id'] for record in cursor]

    def run(self):
        # Get the IDs
        ids = self.get_mp_ids()
        results = self._call_api(id=','.join(ids))

        # Loop through building an array, with _id set to key (person_id)
        data = []
        for key, record in results.iteritems():
            record['_id'] = key
            data.append(record)

        self.get_collection().insert(data)


if __name__ == "__main__":
    luigi.run(main_task_cls=TheyWorkForYouGetMPInfoTask)