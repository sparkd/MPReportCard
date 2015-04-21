#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os

# TODO: Check we have all IDs for public whip
# select id, name, start_date,party from members where not exists (select 1 from member_twfy where member_id = members.id) order by id;