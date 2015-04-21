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
from mp_data.lib.log import get_logger
from mp_data.model import ConstituencyModel, MemberModel
from mp_data.tasks.local_file import LocalFileTask

log = get_logger(__name__)

class ConstituencyTask(BaseTask):

    """
    Import const

    python tasks/constituency.py --local-scheduler

    """

    model = ConstituencyModel

    def requires(self):

        input_dir = config.get('data', 'input_dir')
        constituency_file = 'Westminster Parliamentary Constituency names and codes UK as at 12_11.txt'
        file_path = os.path.join(input_dir, 'ONSPD_NOV_2013_csv/Documents/Names and Codes', constituency_file)

        yield LocalFileTask(file_path)

    def run(self):
        for input in self.input():
            with input.open('r') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    name = row['PCON11NM'].decode('ISO-8859-1').encode('utf-8')
                    self.db_session.add(self.model(
                        id=row['PCON11CD'],
                        name=name.strip(),
                    ))

        self.db_session.commit()

if __name__ == "__main__":
    luigi.run(main_task_cls=ConstituencyTask)