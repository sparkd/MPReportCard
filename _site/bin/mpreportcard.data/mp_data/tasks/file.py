#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import luigi
import requests
from mp_data.lib.log import get_logger

log = get_logger(__name__)


class FileTask(luigi.ExternalTask):
    """
    Create a local copy of the EDMS file
    We can then use CSV file formatting and validation
    Otherwise we need to split on lines etc.,
    """

    path = luigi.Parameter()  # Path to the file

    def run(self):

        log.info('Downloading: %s', self.path)

        r = requests.get(self.path)
        r.raise_for_status()

        # Loop through the file, writing to a local copy
        with self.output().open('w') as out_file:

            for block in r.iter_content(1024):
                if not block:
                    break

                out_file.write(block)

    def output(self):

        # Use the same file name as we request

        f = "/tmp/%s" % os.path.basename(self.path)

        if not f.endswith('.csv'):
            f += '.csv'

        return luigi.LocalTarget(f)