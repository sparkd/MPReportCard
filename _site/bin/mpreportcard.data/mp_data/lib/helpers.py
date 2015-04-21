#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import re
import requests
import requests_cache
from bs4 import BeautifulSoup
from mp_data.model import MemberModel, ConstituencyModel, PublicWhipIDModel
from mp_data.db import get_session
from mp_data.data.missing_mps import MISSING_MPS

def ensure_list(l):
    """
    Ensure a var is a list
    @param l:
    @return:
    """
    return l if isinstance(l, list) else [l]

def float_to_int(num):
    """
    Round a float and convert to an int
    :param num:
    :return:
    """
    return int(round(num))

def get_soup(url, key='mps.soup'):
    """
    Helper function to retrieve a web page and return it as soup
    @param url:
    @return: soup
    """

    cache_key = os.path.join('_cache', key)
    requests_cache.install_cache(cache_key)

    r = requests.get(url)
    return BeautifulSoup(r.content, from_encoding='ISO-8859-1')


def get_member_by_name(surname, firstname):
    """
    Look up a member by their name
    @param surname:
    @param firstname:
    @return:
    """

    db_session = get_session()

    q = '%{0}%{1}%'.format(surname, firstname)

    results = db_session.query(MemberModel).filter(MemberModel.list_name.ilike(q)).all()

    # If we have more than one potential match, raise an exception
    assert len(results) < 2, 'MP identifier matched more than one member %s' % results

    try:
        return results[0].id
    except IndexError:
        pass


def get_constituencies():
    """
    Return a dictionary of constituencies, keyed by name
    @return:
    """

    constituencies = {}

    db_session = get_session()

    results = db_session.query(ConstituencyModel).all()

    for result in results:
        constituencies[result.name.lower()] = result.id

    return constituencies


def get_twfy_ids():
    """
    Return a list of MP ids, from the mp_id table
    twfy_id: dods_id
    @return:
    """

    ids = {}
    db_session = get_session()

    result = db_session.execute('SELECT mp.twfy_id, m.id FROM mp_ids mp INNER JOIN members m on m.dods_id = mp.dods_id');

    for record in result:
        ids[record['twfy_id']] = record['id']

    return ids

def get_pw_ids():
    """
    Return a list of public whip => member ID
    pw_id: member_id
    @return:
    """

    ids = {}
    db_session = get_session()

    for record in db_session.query(PublicWhipIDModel).all():
        ids[record.pw_id] = record.member_id

    return ids

def get_number_from_string(string):

    return int(re.search(r'(\d+)', string).group(1))


def list_missing_mp_names():
    """
    List of missing MP names and their aliases
    @return:
    """

    names = []

    for mp_name, mp in MISSING_MPS.items():

        names.append(mp_name)

        # If we have any aliases, add them too
        try:
            for alias in mp['alias']:
                names.append(alias)
        except KeyError:
            pass

    return names






