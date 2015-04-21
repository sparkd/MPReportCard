#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os

# Manually mapped wikipedia URIs
WIKIPEDIA_URLS = {
    25150: "http://en.wikipedia.org/wiki/Seema_Malhotra",
    25067: "http://en.wikipedia.org/wiki/Dan_Jarvis",
    24900: "http://en.wikipedia.org/wiki/Simon_Kirby",
    25227: "http://en.wikipedia.org/wiki/Robert_Jenrick",
    25120: "http://en.wikipedia.org/wiki/Jon_Ashworth",
    24935: "http://en.wikipedia.org/wiki/Steve_Rotheram",
    25220: "http://en.wikipedia.org/wiki/Mike_Kane",
    24874: "http://en.wikipedia.org/wiki/Simon_Wright_(politician)",
    25169: "http://en.wikipedia.org/wiki/Andy_McDonald_(politician)",
    25168: "http://en.wikipedia.org/wiki/Sarah_Champion_(politician)",
    25167: "http://en.wikipedia.org/wiki/Andy_Sawford",
    25166: "http://en.wikipedia.org/wiki/Stephen_Doughty",
    25165: "http://en.wikipedia.org/wiki/Lucy_Powell",
    24788: "http://en.wikipedia.org/wiki/Shabana_Mahmood",
    25181: "http://en.wikipedia.org/wiki/Emma_Lewell-Buck",
    25230: "http://en.wikipedia.org/wiki/Liz_McInnes",
    25034: "http://en.wikipedia.org/wiki/Debbie_Abrahams",
    24924: "http://en.wikipedia.org/wiki/Luciana_Berger",
    24819: "http://en.wikipedia.org/wiki/Ian_Swales",
    25175: "http://en.wikipedia.org/wiki/Mike_Thornton_(politician)",
    24825: "http://en.wikipedia.org/wiki/Jack_Dromey",
    25170: "http://en.wikipedia.org/wiki/Steve_Reed_(politician)",
    24910: "http://en.wikipedia.org/wiki/Caroline_Lucas",
    25145: "http://en.wikipedia.org/wiki/Iain_McKenzie",
    # There is an error in wikipedia redirection for http://en.wikipedia.org/wiki/Julian_Lewis_(MP)
    # So we're going to have to specify the page id instead
    10358: 428630
}
