#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os





FINANCIAL_INTEREST_ERRORS = {
    'reeves_rachel': {
        '{"date": "5 November 2012", "name": "PricewaterhouseCoopers LLP"}': {
            'date': '5 November 2012',
            'value': 25162.50
        },
        '{"date": "8 June 2012", "name": "PricewaterhouseCoopers LLP"}': {
            'value': 25162.50
        }
    },
    'umunna_chuka': {
        '{"date": "8 November 2012", "name": "PricewaterhouseCoopers LLP"}': {
            'date': '8 November 2012',
            'value': 25162.50
        }
    },
    'hands_greg': {
        '{"date": "6 June 2012", "name": "Mr Arunasalam Yogeswaran"}': {
            'date': '8 November 2012',
            'value': 4942
        },
        '{"date": "1 August 2011", "name": "Mr Arunasalam Yogeswaran"}':{
            'value': 11134.70
        }
    },
    'crabb_stephen':{
        '{"date": "5 July 2011", "value": 5841.86}':{
            'name': 'Unknown (not stated)'  # There is no name of donor entry
        }
    },
    'farron_tim':{
        '{"date": "14 October 2011", "name": "CARE"}':{
            'value': 0  # There is no value specified - and is a voluntary intern so 0?
        }
    },
    'phillipson_bridget': {
        '{"date": "29 June 2011", "value": 424.68}':{
            'name': 'Fundraising dinner'
        },
        '{"date": "29 June 2011", "value": 2123.4}':{
            'name': 'Free use of PoliticsHome Pro service'
        }
    },
    'smith_julian': {
        '{"date": "30 March 2011", "name": "Skipton Building Society"}':{
            'value': 2407.75
        }
    },
    'raab_dominic': {
        '{"date": "12 March 2013", "name": "Esher and Walton Connect"}':{
            'value': 4838.48
        },
        '{"date": "26 February 2014", "name": "Esher and Walton Connect"}':{
            'value': 7273.08
        }
    },
    'cable_vincent': {
        '{"date": "8 April 2010", "name": "PricewaterhouseCoopers"}':{
            'value': 78710
        }
    },
    'gove_michael': {
        '{"name": "Digital Delivery Development Ltd", "value": 2000.0}':{
            'date': '1 June 2010'  # In the register as I June 2010
        }
    },
    'eagle_angela': {
        '{"date": "4 June 2010", "name": "PricewaterhouseCoopers"}':{
            'value': 0  # No value specified
        }
    },
    'maude_francis': {
        '{"date": "2 February 2010"}':{
            'value': 0,  # No value specified
            'name': 'Unknown' # No information provided
        },
        '{"date": "3 February 2010", "name": "Boston Consulting Group (consultancy)"}':{
            'value': 79411.12
        }
    },
    'balls_ed': {
        '{"name": "Ken Follett", "value": 11000.0}': {
            'date': '3 November 2010'  # No value specified
        }
    },
    'macleod_mary': {
        '{"name": "Heathrow Airport Limited\\n\\nAddress of donor: The Compass Centre, Nelson Road, Hounslow, Middlesex TW6 2GW\\n\\n\\n\\nAmount of donation or nature and value if donation in kind: \\u00c2\\u00a35,000; sponsorship for 2014 West London Jobs and Apprenticeships Fair", "value": 5000.0}': {
            'date': '19 December 2013'
        }
    },
    'weatherley_mike':{
        '{"name": "Theodore Fraser", "value": 2500.0}':{
            'date': '18 December 2013'
        },
        '{"name": "Stewart Newton", "value": 10000.0}':{
            'date': '18 December 2013'
        },
        '{"name": "Ray Bloom", "value": 2500.0}':{
            'date': '18 December 2013'
        }
    },
    'yeo_tim':{
        '{"date": "1 June 2013", "description": "Chairman of Albion Community Power PLC, independent generator of renewable energy (from 30 May 2013 until 20 June 2013).  Address: 1 King\\u00e2\\u0080\\u0099s Arms Yard, London EC2R 7AF.  (Registered 1 June 2013; updated 3 February 2014)"}':{
            'value': 0  # No value specified
        },
        },
    'simpson_keith': {
        '{"description": "Book Review Editor at\\n \\nTotal Politics magazine, 375 Kennin\\ngton Lane London SE11 5QY. Paid\\n \\u00c2\\u00a3145 per month, until further notice. Hours: approximately 20\\n \\nhrs per month.", "value": 145.0}':{
            'date': '1 January 2015',  # Default date
            'value': 1740  # This is actually 145 per month
        }
    },
    'rifkind_malcolm':{
        '{"description": "Senior Counsellor, Dragoman, Collins Street, Melbourne, Australia, specialist advisory firm. No regular meetings, communication by email and occasional meetings in London as might be required. Retainer of Australian $12,500 paid every three months."}':{
            'value': 25808,  # $12,500 paid every three months
            'date': '1 January 2015',  # Default date
        },
        },
    'brady_graham':{
        '{"description": "Fee of \\u00c2\\u00a375 paid direct to charity on 29 September 2014 for September Panel survey.", "value": 75.0}':{
            'date': '7 October 2014',
            }
    },
    'brown_gordon':{
        '{"description": "Airfare and accommodation in Istanbul, Turkey also paid for me and my staff; \u00c2\u00a33,461.73. (Registered 17 November)", "value": 3461.73}':{
            'date': '17 November 2014',
            },
        '{"description": "Airfare and accommodation in Washington, USA also paid for me and my staff; \u00c2\u00a312,624.29. (Registered 17 November)", "value": 12624.29}':{
            'date': '17 November 2014',
            }
    },
    # 'GALLOWAY, George':{
    #     '{"description": "Received \\u00c2\\u00a36,000 and return flights London to Beirut (value approx \\u00c2\\u00a3600) in", "value": 6000.0}':{
    #         'date': '12 February 2014'
    #     },
    #     '{"description": "Payment of \\u00c2\\u00a3900 received from Fairpley, 19 Marine Crescent, Glasgow G51 1HD,", "value": 900.0}':{
    #         'date': '20 February 2014'
    #     }
    # },
    'hancock_michael':{
        '{"description": "December 2013, received basic allowance of \\u00c2\\u00a3850 and a special responsibility", "value": 850.0}':{
            'date': '13 January 2014',
            'value': 1445
        },
        '{"description": "January 2014, received basic allowance of \\u00c2\\u00a3850 and a special responsibility", "value": 850.0}':{
            'date': '13 January 2014',
            'value': 1445
        },
        '{"description": "February 2014 received basic allowance of \\u00c2\\u00a3850 and a special responsibility", "value": 850.0}':{
            'date': '28 February 2014',
            'value': 1445
        }
    },
    'brown_nicholas' :{
        '{"date": "21 August 2014", "value": 2000.0}':{
            'name': 'Japan Tobacco International',
        }
    },
    'cameron_david' :{
        '{"date": "14 December 2009"}':{
            'value': 4000,
            'name': 'Painting by Abdul Rahim Salem, kindly given to me by His Highness, Sheikh Mohammed bin Rashid Al Maktoum, Vice President and Prime Minister of United Arab Emirates, and Ruler of Dubai',
            'donated_to_charity': True
        }
    },
    'hendrick_mark' :{
        '{"date": "6 September 2011", "value": 733.0}':{
            'name': 'London South Bank University; (2) Hanban; (3) Huawei'
        }
    },
    'banks_gordon' :{
        '{"name": "J M McGregor", "value": 2000.0}':{
            'date': '8 June 2010',
        }
    },
    'james_margot' :{
        '{"name": "Folkes Ltd; engineering and property", "value": 3300.0}':{
            'date': '8 June 2010',
        }
    }




}