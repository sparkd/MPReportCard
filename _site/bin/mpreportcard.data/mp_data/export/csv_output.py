#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import csv
import unicodecsv
import itertools
from mp_data.db import get_session
from mp_data import config, MP_COUNT
from mp_data.model import *
from mp_data.lib.helpers import float_to_int
from sqlalchemy import and_, func, cast, Integer
from sqlalchemy.orm.exc import NoResultFound


class CSV(object):

    def __init__(self, query, file_name):

        self.query = query

        directory = os.path.join(config.get('data', 'output_dir'), 'data')

        if not os.path.exists(directory):
            os.makedirs(directory)

        self.outfile = os.path.join(directory, file_name)

    def run(self):

        with open(self.outfile, 'wb') as f:

            writer = unicodecsv.writer(f, encoding='utf-8')

            # Write the headers
            writer.writerow([col.get('name') for col in self.query.column_descriptions])

            for member in self.query:

                line = []

                # Loop through each value and try and fix the encoding
                for value in member:
                    try:
                        value = unicode(value.encode('latin-1', 'ignore'), "utf-8", 'ignore')
                    except AttributeError:
                        pass
                    finally:
                        line.append(value)

                writer.writerow(line)

            print 'Output to: %s' % self.outfile