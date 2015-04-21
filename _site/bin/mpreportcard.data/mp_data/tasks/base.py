#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import luigi
import abc
from mp_data.db import get_session

class BaseTask(luigi.Task):
    """
    Base task
    """

    # If set, delete first
    delete = luigi.BooleanParameter(default=False)

    progress_count = 0

    def __init__(self, *args, **kwargs):

        super(BaseTask, self).__init__(*args, **kwargs)
        self.db_session = get_session()

    def complete(self):

        if self.delete:
            self.delete_entries()
        elif self.count_entries():
            return True

        return False

    @abc.abstractproperty
    def model(self):
        """
        Model
        Used in delete query and create queries
        @return:
        """
        return None

    def _query(self):
        """
        Build a query to select based on the parameters
        If --delete is set, this will be used to delete entries
        Otherwise it will be used to check if the task needs to run
        @return:
        """
        q = self.db_session.query(self.model)

        # Before running, delete any existing entries
        # Filtering on an parameters we've passed in
        for param, _ in self.get_params():
            # Are we running this task for a particular mp or yearly session
            # If so add the filters

            # Check the model has the attr - we can then have params only used in import
            if getattr(self, param) and hasattr(self.model, param):
                q = q.filter(getattr(self.model, param) == getattr(self, param))

        return q

    def count_entries(self):

        q = self._query()
        return q.count()

    def delete_entries(self):

        q = self._query()
        # And delete the existing entries
        q.delete(synchronize_session=False)
        self.db_session.commit()

    def output_progress(self, modulus=1000):

        self.progress_count += 1

        if self.progress_count % modulus == 0:
            print '%s rows processed' % self.progress_count
