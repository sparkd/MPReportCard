#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import csv
import luigi
import requests
from datetime import datetime
from mp_data.tasks.base import BaseTask
from mp_data.tasks.file import FileTask
from mp_data.lib.log import get_logger
from mp_data.model.expense import ExpenseModel
from mp_data.lib.helpers import get_member_by_name, list_missing_mp_names
from mp_data.data.expense_ids import EXPENSE_IDS

log = get_logger(__name__)

class ExpensesTask(BaseTask):
    """
    Import expenses from http://www.parliamentary-standards.org.uk/DataDownloads.aspx

    python tasks/expenses.py --local-scheduler --session 14_15

    """

    #### Luigi parameters ####
    # Get expenses for a particular session - eg: 14_15
    session = luigi.Parameter(default=None)

    # Get expenses for a particular MP
    mp = luigi.Parameter(default=None)

    model = ExpenseModel

    available_sessions = ['10_11', '11_12', '12_13', '13_14', '14_15']

    members = {}

    def requires(self):

        if self.session:
            assert self.session in self.available_sessions, '%s not an available year' % self.session
            sessions = [self.session]
        else:
            sessions = self.available_sessions

        for session in sessions:
            # The files are actually named by year
            # So 10_11 is 2010
            year = '20%s' % session.split('_')[0]
            url = 'http://www.parliamentary-standards.org.uk/Files/DataDownload_%s.csv' % year
            yield FileTask(url)

    def run(self):

        missing_mp_names = list_missing_mp_names()

        for input in self.input():

            with input.open('r') as in_file:
                reader = csv.DictReader(in_file)

                for row in reader:

                    mp_name = row[" MP's Name"]

                    # If we have specified only one mp and this isn't it, continue
                    if self.mp and self.mp != mp_name:
                        continue

                    # We know we don't have some MPs - so continue
                    if mp_name in missing_mp_names:
                        continue

                    member_id = self.expense_get_member_id(mp_name)

                    if member_id:

                        # Do not insert if we don't have an amount
                        if row[' Amount Paid']:
                            self.db_session.add(self.model(
                                mp=mp_name,
                                member_id=member_id,
                                date=datetime.strptime(row[" Date"], '%d/%m/%Y'),
                                session=row['\xef\xbb\xbfYear'],
                                value=row[' Amount Paid'],
                                claim_number=row[' Claim No.'],
                                category=row[' Category'].lower(),
                                description=row[' Expense Type'],
                            ))

                    else:

                        print 'NO MEMBER ID: %s - %s' % (row['\xef\xbb\xbfYear'], mp_name)
                        raise Exception(mp_name)

                    self.output_progress()

            print 'Committing records'
            self.db_session.commit()

    def expense_get_member_id(self, mp_name):
        """
        Get the member ID for the financial interest
        @param mp_identifier:
        @return:
        """

        member_id = None

        try:
            # Try and return a cached member ID
            return self.members[mp_name]
        except KeyError:
            pass

        try:
            member_id = EXPENSE_IDS[mp_name]
        except KeyError:
            try:
                firstname, surname = mp_name.split(' ')
            except ValueError:
                pass
            else:
                member_id = get_member_by_name(surname, firstname)
        finally:
            # Cache the ID so we don't need to look up again
            self.members[mp_name] = member_id
            return member_id

if __name__ == "__main__":
    luigi.run(main_task_cls=ExpensesTask)