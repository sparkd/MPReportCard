#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import abc
import os
import glob
import luigi
import re
import untangle
from dateutil import parser as date_parser
from urlparse import urlparse
from mp_data import ELECTION_DATE
from mp_data import config
from mp_data.tasks.base import BaseTask
from mp_data.tasks.members import MembersTask
from mp_data.lib.log import get_logger
from mp_data.lib.helpers import get_pw_ids, get_number_from_string
from mp_data.data.missing_mps import MISSING_MPS

log = get_logger(__name__)

class ScrapedXMLTask(BaseTask):

    """
    Uses data downloaded from  data.theyworkforyou.com

      rsync -az --progress --exclude '.svn' --exclude 'tmp/' --relative data.theyworkforyou.com::parldata/scrapedxml/debates/debates201* .

      rsync -az --progress --exclude '.svn' --exclude 'tmp/' --relative data.theyworkforyou.com::parldata/scrapedxml/wrans/answers201* .

    Extended by DebatesScrapedXMLTask and QuestionsScrapedXMLTask

    """

    # Process just one file
    file = luigi.Parameter(default=None)

    @abc.abstractproperty
    def directory(self):
        """
        The name of the directory
        @return:
        """
        return None

    @abc.abstractproperty
    def element_name(self):
        """
        The name of the element to extract
        @return:
        """
        return None

    def requires(self):
        yield MembersTask()

    def input_files(self):

        directory = os.path.join(config.get('data', 'input_dir'), 'scrapedxml', self.directory)
        if self.file:
            yield os.path.join(directory, self.file)
        else:

            files = glob.glob(os.path.join(directory, '*.xml'))

            if not files:
                raise Exception('Import directory %s is empty' % directory)

            for f in files:
                yield f

    def run(self):

        # Create a list of known missing MP pw ids
        known_missing_pw_ids = [mp['pw_id'] for mp in MISSING_MPS.values() if 'pw_id' in mp]

        aliased_ids = {
            # For some reason Diane Abbot has id=1 for older records
            1: 40289,
            # UKIP members - pw_id has changed when they moved parties
            40175: 40703,
            40502: 40704
        }

        # Set UTF-8 for the XML files we're about to read
        reload(sys) # just to be sure
        sys.setdefaultencoding('utf-8')

        # Get the MP ides keyed

        mp_ids = get_pw_ids()

        for f in self.input_files():
            dt = date_parser.parse(re.search(r'(\d{4}-\d{2}-\d{2})', f).group(1))

            # Check this is since the election date
            if dt.date() >= ELECTION_DATE:

                doc = untangle.parse(f)

                try:
                    entries = getattr(doc.publicwhip, self.element_name)
                except IndexError:
                    log.warning('No %s elements in %s', self.element_name, f)
                else:
                    log.info('Processing: %s', f)
                    for entry in entries:

                        data = self.process_entry(entry)
                        data['date'] = dt.date()

                        url = urlparse(entry['url'])

                        # Add debate id just for debates task
                        if self.__class__.__name__ == 'DebatesTask':
                            data['debate_id'] = url.fragment.split('.')[0]

                        try:
                            pw_id = get_number_from_string(entry['speakerid'])

                            if pw_id in aliased_ids:
                                pw_id = aliased_ids[pw_id]

                        except (TypeError, AttributeError):
                            continue
                        try:
                            # Get the member ID that matches the public whip id
                            data['member_id'] = mp_ids[pw_id]
                        except KeyError:

                            if pw_id not in known_missing_pw_ids:
                                raise Exception('Missing PW ID %s' % pw_id)

                        else:
                            self.db_session.add(self.model(**data))

            self.db_session.commit()

    def process_entry(self, entry):
        # Default impl;
        return {}


if __name__ == "__main__":
    luigi.run(main_task_cls=ScrapedXMLTask)