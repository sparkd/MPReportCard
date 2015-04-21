#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
import csv
import luigi
import urlparse
from sqlalchemy import func, exists
from mp_data.tasks.base import BaseTask
from mp_data.lib.log import get_logger
from mp_data.model import PublicWhipIDModel, MemberModel
from mp_data.lib.helpers import get_twfy_ids, get_soup


log = get_logger(__name__)


class PublicWhipIDTask(BaseTask):

    """
    The theyworkforyou pages have link to the public whip pages
    So for each mp, get the theyworkforyou page, and parse the link
    http://www.theyworkforyou.com/mp/10858/pat_doherty/west_tyrone
    """

    session = luigi.Parameter(default=None)  # 12-13 - see available_sessions

    model = PublicWhipIDModel

    def complete(self):

        # select id, name, start_date,party from members where not exists (select 1 from member_twfy where member_id = members.id) order by id;
        count = self.db_session.query(func.count('*')).select_from(MemberModel).filter(
            ~exists().where(
                PublicWhipIDModel.member_id == MemberModel.id
            )
        ).scalar()

        # If we have any members without a corresponding public whip id, this task is not complete
        return False if count else True

    def run(self):

        mp_ids = get_twfy_ids()

        for twfy_id, member_id in mp_ids.items():

            url = 'http://www.theyworkforyou.com/mp/%s' % twfy_id
            log.info('Processing page: %s', url)

            soup = get_soup(url)

            try:
                link = soup.find("div", {"class": "panel--secondary"}).find('a')
            except AttributeError:
                # We have one error on page http://www.theyworkforyou.com/mp/10913/michelle_gildernew/fermanagh_and_south_tyrone
                if twfy_id == 10913:
                    public_whip_id = 40259
            else:

                parsed_url = urlparse.urlparse(link.get("href"))

                # Make sure this is a link to the public whip site
                assert 'publicwhip.org.uk' in parsed_url.netloc

                query = urlparse.parse_qs(parsed_url.query)
                # GET Number
                public_whip_id = re.search(r'(\d+)', query['id'][0]).group(1)

            self.db_session.add(self.model(pw_id=public_whip_id, member_id=member_id))

        self.db_session.commit()


if __name__ == "__main__":
    luigi.run(main_task_cls=PublicWhipIDTask)