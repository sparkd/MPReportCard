#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import wikipedia
from mp_data.data.wikipedia_urls import WIKIPEDIA_URLS
from mp_data.tasks.theyworkforyou import TheyWorkForYouGetMPInfoTask, TheyWorkForYouGetMPTask

def main():

    """
    Output a list of MPs names with missing wikipedia pages
    We can then manually look them up & add to mp_data.data.wikipedia
    @return:
    """
    info_collection = TheyWorkForYouGetMPInfoTask().get_collection()

    mp_collection = TheyWorkForYouGetMPTask().get_collection()

    cursor = info_collection.find({}, {'wikipedia_url': True})

    missing_ids = []

    for record in cursor:

        try:
            record['wikipedia_url']
        except KeyError:

            if int(record['_id']) not in WIKIPEDIA_URLS:

                # If we don't have a wikipedia URL, look up the name
                mp = mp_collection.find_one({'_id': record['_id']}, {'name': True})

                print 'Missing wikipedia URL for: %s' % mp['name']
                print record['_id']
                missing_ids.append(record['_id'])

                # List a look up of potential pages
                for result in wikipedia.search('%s MP' % mp['name']):
                    print '\thttp://en.wikipedia.org/wiki/%s' % result.encode('utf-8').replace(' ', '_')

                print '------'

    for id in missing_ids:
        print '\t%s: "",' % id


if __name__ == '__main__':
    main()

