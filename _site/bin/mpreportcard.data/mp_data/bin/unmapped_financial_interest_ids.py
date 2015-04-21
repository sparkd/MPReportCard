#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from mp_data.tasks.financial_interests import FinancialInterestsTask

def main():
    """
    Loop through the financial interest pages, and seeing if we can match the
    MP identifier against a name in our members table

    If we can't find a match, print out error and at the end
    a dictionary to use for manual mapping

    @return:
    """
    task = FinancialInterestsTask()

    # Just get the last session (24-14-15)
    session, register_url = task.registers.next()

    for url in task.get_register_mp_urls(register_url):
        mp_identifier = task.get_mp_identifier_from_url(url)
        member_id = task.get_member_id(mp_identifier)
        if not member_id:
            print "'%s':," % mp_identifier

if __name__ == '__main__':
    main()

