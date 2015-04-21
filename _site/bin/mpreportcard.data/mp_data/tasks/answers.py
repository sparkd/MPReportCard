#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import luigi
from mp_data.tasks.scraped_xml import ScrapedXMLTask
from mp_data.model import AnswerModel

class AnswersTask(ScrapedXMLTask):

    """
    Import debates data.theyworkforyou.com::parldata/scrapedxml/debates/debates201

    python tasks/answers.py --local-scheduler

    """

    directory = 'wrans'
    element_name = 'ques'
    model = AnswerModel

    def process_entry(self, entry):
        data = {}
        # Loop through the text, checking for [R] tag
        # Meaning the question has been asked for a registered interest
        for p in entry.p:
            if '[R]' in p.cdata:
                data['registered_interest'] = True

        return data

if __name__ == "__main__":
    luigi.run(main_task_cls=AnswersTask)