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
    query = session.query(
        MemberModel.id,
        MemberModel.list_name,
        MemberModel.party,
        FinancialInterestModel.session,
        FinancialInterestModel.type,
        FinancialInterestModel.date,
        FinancialInterestModel.value,
        FinancialInterestModel.donated_to_charity,
        FinancialInterestModel.party_donation,
        FinancialInterestModel.description,
        FinancialInterestModel.sub_entry
    ).join(FinancialInterestModel)

    csv = CSV(query, 'financial-interests.csv')
    csv.run()

if __name__ == '__main__':
    main()

