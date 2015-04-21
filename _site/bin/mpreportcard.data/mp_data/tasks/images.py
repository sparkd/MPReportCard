#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
import glob
import os
import luigi
import urllib2
import shutil
import wikipedia as wikipedia_api
from PIL import Image
from mp_data.model import MemberModel
from mp_data.db import get_session
from mp_data.lib.helpers import get_twfy_ids
from mp_data.lib.log import get_logger
from mp_data.tasks.theyworkforyou import TheyWorkForYouGetMPInfoTask
from mp_data.data.wikipedia_urls import WIKIPEDIA_URLS
from mp_data import config

log = get_logger(__name__)

class ImagesTask(luigi.Task):

    """
    Try and download images from wikipedia
    If there's no images on wikipedia, download from www.edms.org.uk (bad quality)

    python tasks/images.py --local-scheduler

    """

    id = luigi.IntParameter(default=None)

    thumbnail_size = 120, 120

    def __init__(self, *args, **kwargs):

        super(ImagesTask, self).__init__(*args, **kwargs)

        # Define the output dir, and create it if it doesn't exist
        self.output_dir = os.path.join(config.get('data', 'output_dir'), 'images')

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def requires(self):
        yield TheyWorkForYouGetMPInfoTask()

    def get_wikipedia_ids(self, twfy_id):

        info_collection = TheyWorkForYouGetMPInfoTask().get_collection()

        q = {'_id': str(twfy_id)}

        cursor = info_collection.find(q, {'wikipedia_url': True})

        # Regex to replace brackets and dashes
        regex = re.compile(r"\(|\)|-", re.IGNORECASE)

        for record in cursor:

            # First look up against our manual URLs
            # This allows us to over write the ones we've retrieved from they work for you
            # EG: Paul_Murphy_(UK_politician) => http://en.wikipedia.org/wiki/Paul_Murphy_(British_politician)
            try:
                url = WIKIPEDIA_URLS[int(record['_id'])]
            except KeyError:
                url = record['wikipedia_url']

            # If this is a string (we do allow page ids in WIKIPEDIA_URLS)
            if isinstance(url, basestring):

                # Get the last part of the URL - this is the wikipedia ID
                wikipedia_id = url.split('/')[-1]

                # The ID doesn't contain parenthesis
                wikipedia_id = regex.sub('', wikipedia_id)
                wikipedia_id = wikipedia_id.replace("%27", "'")

                yield wikipedia_id

    def run(self):

        print 'NOT RUNNING'
        return

        twfy_ids = get_twfy_ids()

        for twfy_id, member_id in twfy_ids.items():

            wikipedia_ids = self.get_wikipedia_ids(twfy_id)

            for wikipedia_id in wikipedia_ids:
                # If we have specified the numeric ID, use that
                # Otherwise load by normal page id
                if isinstance(wikipedia_id, int):
                    params = {'pageid': wikipedia_id}
                else:
                    params = {'title': wikipedia_id}

                # Set a flag for whether we've found a wikipedia image
                has_wikipedia_image = False

                # Load the wikipedia page
                try:
                    page = wikipedia_api.page(**params)
                except wikipedia_api.PageError, e:
                    print e
                else:
                    for i, wikipedia_image in enumerate(page.images):
                        file_name, file_extension = os.path.splitext(wikipedia_image)
                        if file_extension == '.jpg':

                            # For the first image, we'll just use member_id
                            # But for subsequent files, we'll add the key so
                            # They are available but not overwritten
                            local_file_name = str(member_id)

                            if has_wikipedia_image:
                                local_file_name += '-%s' % i

                            self.copy_image_to_local(wikipedia_image, local_file_name)

                            has_wikipedia_image = True

            # If we haven't found a wikipedia image, we'll use ones from http://www.edms.org.uk/data/
            if not has_wikipedia_image:
                self.copy_image_to_local('http://www.edms.org.uk/images/mps/%s.jpg' % twfy_id, str(member_id))


    def copy_image_to_local(self, remote_url, local_file_name):

        # To speed this up, we want to check if we have the file before
        # opening a connection to it.  We don't know the file extension
        # at this point, so use glob to check

        # File name without extension
        local_file_no_ext = os.path.join(self.output_dir, '%s' % (local_file_name))
        existing = glob.glob('%s.*' % local_file_no_ext)

        # If we do not have the file, download it
        if existing:

            # This should always be one
            assert len(existing) == 1
            local_file = existing[0]

        else:

            try:
                remote_file = urllib2.urlopen(remote_url)
            except urllib2.HTTPError, e:
                print 'Error downloading file %s' % remote_url
                print local_file_name
                print e
                print '-----'
                return
            else:
                _, file_extension = os.path.splitext(remote_url)
                local_file = os.path.join(self.output_dir, '%s%s' % (local_file_name, file_extension))

                log.info('Downloading file %s to %s', remote_url, local_file_name)

                with open(local_file, 'wb') as f:
                    shutil.copyfileobj(remote_file, f)

        # Resize the image if we need to - do this for all files even existing
        # So we can run this against existing
        resize = True
        img = Image.open(local_file)
        for i, size in enumerate(self.thumbnail_size):
            # We're thumbnailing, so the image has already been resized
            # If any one of the dimensions is an appropriate size
            if img.size[i] == size:
                resize = False
                break

        if resize:
            log.info('Resizing image: %s', local_file_name)
            img.thumbnail(self.thumbnail_size, Image.ANTIALIAS)
            img.save(local_file)

    def on_success(self):
        """
        On success, check we have an image for every MP
        :return:
        """
        db_session = get_session()

        results = db_session.query(MemberModel).filter().all()

        for member in results:

            # File name without extension
            f = os.path.join(self.output_dir, '%s' % (member.id))

            if not glob.glob('%s.*' % f):
                print 'MISSING IMAGE FOR MEMBER: %s %s' % (member.name, member.id)

        print 'SUCCESS'



if __name__ == "__main__":
    luigi.run(main_task_cls=ImagesTask)