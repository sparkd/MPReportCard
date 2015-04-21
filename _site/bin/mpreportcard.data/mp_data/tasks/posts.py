#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import re
import luigi
import requests
import requests_cache
from mp_data.tasks.base import BaseTask
from mp_data.lib.log import get_logger
from mp_data.model import PostModel
from mp_data.lib.helpers import ensure_list
from mp_data.tasks.members import MembersTask

log = get_logger(__name__)

requests_cache.install_cache('_cache/data.parliament.posts')

class PostsTask(MembersTask):

    """
    Get members from http://data.parliament.uk/membersdataplatform/memberquery.aspx#outputs
    python tasks/members.py --local-scheduler
    """

    model = PostModel

    # Member id
    id = luigi.IntParameter(default=None)

    def requires(self):
        yield MembersTask()

    def run(self):

        for member in self._request('GovernmentPosts|OppositionPosts|ParliamentaryPosts'):

            member_id = int(member['@Member_Id'])

            for post_type in ['OppositionPosts', 'GovernmentPosts', 'ParliamentaryPosts']:
                if member[post_type]:

                    for post in ensure_list(next(member[post_type].itervalues())):

                        self.db_session.add(self.model(
                            member_id=member_id,
                            title=post['Name'],
                            start_date=post[u'StartDate'],
                            end_date=post[u'EndDate'],
                            type=post_type.replace('Posts', '').lower()
                        ))

        self.db_session.commit()


if __name__ == "__main__":
    luigi.run(main_task_cls=PostsTask)