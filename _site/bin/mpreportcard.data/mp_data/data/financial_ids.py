#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os

# Manual mapping of IDs we can't find via a DB lookup - see financial_interest_get_member_id()

FINANCIAL_INTEREST_IDS = {
    'byles_daniel':4112,
    'clegg_nicholas':1563,
    'coffey_therese':4098,
    'dakin_nick':4056,
    'hancock_michael':59,
    'james_sian':1573,
    'kendall_elizabeth':4026,
    'leslie_christopher':422,
    'mccabe_stephen':298,
    'obrien_stephen':427,
    'odonnell_fiona':3964,
    'slaughter_andrew':1516,
    'watts_david':489,
    'wishart_peter':1440,
    'baker_steven': 4064,
    'cable_vincent': 207,
    'onwurah_chinyelu': 4124,
    'smith_': 3928,
    'gummer_benedict': 3988,
    'lee_philip': 3921,
}