#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os

# Manual mapping of IDs we can't find via a DB lookup - see expense_get_member_id()
# None are one we know about, but don't include (deceased etc.,)

EXPENSE_IDS = {
'Nick Dakin':4056,
'Daniel Byles':4112,
'Therese Coffey':4098,
'Christopher Leslie':422,
'Bob Neill':1601,
# 'Jim Dobbin': None,
'Vincent Cable':207,
'Stephen McCabe':298,
# 'Patrick Mercer': None,
'Willie Bain':1610,
'Andy Love':164,
'Sylvia Hermon':1437,
'Bill Cash':288,
# 'Paul Goggins': None,
'Chinyelu Onwurah':4124,
'Gloria De Piero':3915,
'Nick de Bois':4002,
'Iain Duncan Smith':152,
}

