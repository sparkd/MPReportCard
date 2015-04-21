#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from mp_data.db import get_session
from mp_data.export.csv_output import CSV
from mp_data.model import *

def main():
    """
    Create CSV dataset to upload to github
    @return:
    """
    session = get_session()

    members = session.query(
        MemberModel.id,
        MemberModel.list_name,
    )

    base_query = session.query(
        MemberModel.id,
        MemberModel.list_name,
        MemberModel.party,
        ExpenseModel.session,
        ExpenseModel.date,
        ExpenseModel.value,
        ExpenseModel.category,
        ExpenseModel.description,
        ExpenseModel.claim_number
    ).join(ExpenseModel)

    for member in members:
        query = base_query.filter(ExpenseModel.member_id == member.id)
        print 'Exporting %s' % member.list_name
        csv = CSV(query, '%s.csv' % member.list_name.lower().replace(',', '').replace(' ', '_'))
        csv.run()

if __name__ == '__main__':
    main()

