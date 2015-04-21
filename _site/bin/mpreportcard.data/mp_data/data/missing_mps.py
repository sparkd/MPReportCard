#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os

# List of MPs we're not interested in - no longer in power
MISSING_MPS = [


    # 'Martin McGuinness',
    #
    # 'Louise Bagshawe',
    #

    # 'Marsha Singh',
    #
    #
    # 'Gerry Adams'
]

FORCED_RESIGNATION = 0  # Sacked / forced to resign
STEPPED_DOWN = 1  # Stepped down / retired
DIED = 2
DEFECTED = 3  # Transferred to another party
IMPRISONED = 4  # Resigned before being locked up
RENAMED = 5  # Married and renamed


MISSING_MPS = {
    # These have been derived from the scraped_xml based imports
    'Patrick Mercer': {
        'pw_id': 40417,
        'reason': FORCED_RESIGNATION,
        'details': 'For making "unacceptable" racist remarks'
    },
    'Tony Lloyd': {
        'pw_id': 40386,
        'reason': STEPPED_DOWN,
        'details': 'To stand for Greater Manchester Police and Crime Commissioner'
    },
    'Mike Hancock': {
        'pw_id': 40486,
        'reason': FORCED_RESIGNATION,
        'details': 'Forced to resign from the liberal democrats. Now an independent'
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40679
    'Paul Goggins': {
        'pw_id': 40679,
        'reason': DIED
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40552
    'David Miliband': {
        'pw_id': 40552,
        'reason': STEPPED_DOWN
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40330
    'David Cairns': {
        'pw_id': 40330,
        'reason': DIED
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40359
    'Peter Soulsby': {
        'pw_id': 40359,
        'reason': STEPPED_DOWN,
        'details': 'Contest mayor of Leicester'
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40236
    'Christopher Huhne': {
        'pw_id': 40236,
        'reason': IMPRISONED,
        'alias': ['Chris Huhne']
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40258
    'Alan Keen': {
        'pw_id': 40258,
        'reason': DIED
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40400
    'Stuart Bell': {
        'pw_id': 40400,
        'reason': DIED
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40147
    'Alun Michael': {
        'pw_id': 40147,
        'reason': STEPPED_DOWN,
        'details': 'To stand for Police and Crime Commissioner for South Wales'
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40184
    'Louise Mensch': {
        'pw_id': 40184,
        'reason': STEPPED_DOWN
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40467
    'Phil Woolas': {
        'pw_id': 40467,
        'reason': FORCED_RESIGNATION,
        'details': 'On 5 November 2010, he was found to have breached the Representation of the People Act 1983 in the course of the 2010 general election. As a result his victory at the 2010 general election campaign was declared void'
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40316
    'Jim Dobbin': {
        'pw_id': 40316,
        'reason': DIED
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40509
    'Denis MacShane': {
        'pw_id': 40509,
        'reason': IMPRISONED,
        'details': 'On 18 November 2013 he pleaded guilty to false accounting at the Old Bailey, by submitting false receipts for £12,900,[6] and on 23 December 2013, he was sentenced to six months imprisonment.'
    },
    # http://www.publicwhip.org.uk/mp.php?id=uk.org.publicwhip/member/40191
    'Malcolm Wicks': {
        'pw_id': 40191,
        'reason': DIED
    },
    # These are missing from the expenses import.
    # I haven't added the pw_id as I'd like to know if these missing ones flag up
    # anywhere other than the expenses
    'Marsha Singh':{
        'reason': DIED
    },
    'Eric Illsley':{
        'pw_id': 40056,
        'reason': IMPRISONED,
        'details': 'Pleaded guilty to three counts of false accounting on 11 January 2011, he became the first sitting Member of Parliament to be convicted of a criminal offence in the scandal.'
    },
    'Martin McGuinness':{
        'reason': STEPPED_DOWN,
        'details': 'To become Deputy First Minister of Northern Ireland'
    },
    # Mensch
    'Louise Bagshawe':{
        'reason': RENAMED
    },
    'Gerry Adams':{
        'reason': STEPPED_DOWN,
        'details': 'President of Sinn Féin'
    },

}

