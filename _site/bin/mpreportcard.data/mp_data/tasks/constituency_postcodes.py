#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import csv
import urllib
import luigi
from mp_data import config
from mp_data.tasks.base import BaseTask
from mp_data.tasks.constituency import ConstituencyTask
from mp_data.lib.log import get_logger
from mp_data.lib.helpers import get_constituencies
from mp_data.model import ConstituencyPostcodeModel
from mp_data.tasks.local_file import LocalFileTask

log = get_logger(__name__)

class ConstituencyPostcodesTask(BaseTask):

    """
    Import constituency postcodes

    python tasks/constituency_postcodes.py --local-scheduler

    """

    model = ConstituencyPostcodeModel

    def requires(self):

        input_dir = config.get('data', 'input_dir')
        file_path = os.path.join(input_dir, 'ONSPD_NOV_2013_csv/Data/ONSPD_NOV_2013_UK.csv')
        return ConstituencyTask(), LocalFileTask(file_path)

    def run(self):

        constituencies = get_constituencies().values()

        for input in self.input():
            # Skip the constituency dependency
            if isinstance(input, luigi.file.LocalTarget):
                with input.open('r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:

                        # Some are missing the postcode
                        if row['pcon']:

                            # Make sure we have a correct constituency ID
                            if row['pcon'] in constituencies:
                                self.db_session.add(self.model(
                                    constituency_id=row['pcon'],
                                    postcode=row['pcd'].replace(' ', '')  # There are three postcode columns - pcd2 & pcds are always the same as pcd
                                ))

                                self.output_progress()

                            else:

                                log.error('%s not a constituency', row['pcon'])
                                continue

                            # Commit every 10000
                            if self.progress_count % 10000 == 0:
                                log.info('Committing records')
                                self.db_session.commit()

        self.db_session.commit()

if __name__ == "__main__":
    luigi.run(main_task_cls=ConstituencyPostcodesTask)