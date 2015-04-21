#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import luigi
from mp_data.tasks.scraped_xml import ScrapedXMLTask
from mp_data.model import DebateModel


class DebatesTask(ScrapedXMLTask):

    """
    Import debates data.theyworkforyou.com::parldata/scrapedxml/debates/debates201

    python tasks/debates.py --local-scheduler

    """

    directory = 'debates'
    element_name = 'speech'
    model = DebateModel

if __name__ == "__main__":
    luigi.run(main_task_cls=DebatesTask)