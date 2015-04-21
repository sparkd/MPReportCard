#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import re
from sqlalchemy import distinct, not_
from mp_data.db import get_session
from mp_data.model import ExpenseModel, MemberModel
from mp_data.tasks.expenses import ExpensesTask

def main():
    """
    Join up the expenses MP name with the member ID - Used to create the dict

    @return:
    """

    db_session = get_session()

    # Get a list of distinct MP names
    # .filter(ExpenseModel.session == '14_15')
    mp_names = db_session.query(distinct(ExpenseModel.mp)).all()

    print 'Number of MPs with expenses: %s' % len(mp_names)

    ids = []

    for mp_name in mp_names:

        member_id = expense_get_member_id(mp_name[0].encode('utf-8'))

        if not member_id:
            print "'%s':," % mp_name
        else:
            ids.append(member_id)

    # Do we have any members without expenses?

    missing_members = db_session.query(MemberModel).filter(not_(MemberModel.id.in_(ids))).all()

    print 'Members without expenses:'
    for member in missing_members:
        print "\t", member.name



if __name__ == '__main__':
    main()

