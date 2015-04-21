#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
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

db_session = get_session()


def main():
    """
    Create CSV dataset to upload to github
    @return:
    """

    directory = os.path.join(config.get('data', 'output_dir'), 'images')

    members = db_session.query(MemberModel).all()

    ids = []

    for m in members:

        ids.append(m.id)

        image = os.path.join(directory, '%s.jpg' % m.id)

        if not os.path.isfile(image):
            print 'Missing image for MP %s: %s' % (m.id, m.name)


    for fn in os.listdir(directory):

        try:
            mid = re.match(r'([\d]+)', fn).group(1)
            if int(mid) not in ids:
                # Delete file - no member
                print 'Deleting file for member %s' % mid
                os.remove(os.path.join(directory, fn))

        except AttributeError:
            pass

        # print fn
         # if os.path.isfile(fn):
         #    print (fn)

if __name__ == '__main__':
    main()

