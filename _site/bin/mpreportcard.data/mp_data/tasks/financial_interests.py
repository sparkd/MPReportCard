#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import re
import luigi
import requests
import json
import calendar
from bs4 import BeautifulSoup
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
from mp_data.tasks.base import BaseTask
from mp_data.lib.log import get_logger
from mp_data.model.financial_interest import *
from mp_data.lib.helpers import get_member_by_name, get_soup, list_missing_mp_names
from mp_data.data.financial_interest_errors import FINANCIAL_INTEREST_ERRORS
from mp_data.data.financial_ids import FINANCIAL_INTEREST_IDS

log = get_logger(__name__)

class FinancialInterestsTask(BaseTask):
    """
    Import financial interests from http://www.publications.parliament.uk/pa/cm/cmregmem.htm

    python tasks/financial_interests.py --local-scheduler --session 2014-15 --mp danczuk_simon --interest-type 5

    """

    #### Luigi parameters ####
    # Get interests for a particular session - eg: 2010-11
    session = luigi.Parameter(default=None)
    # Get interests for a particular MP
    mp = luigi.Parameter(default=None)
    # Process only a particular interest type
    interest_type = luigi.IntParameter(default=None)

    #### BaseTask parameters ####
    # Set the model to base FinancialInterestModel so delete method works
    model = FinancialInterestModel

    #### Regular expressions parsers ####
    regex = dict()
    regex['mp_name'] = re.compile('.+, .+')
    # Extract session from title
    # session 2013-14 => 2013-14
    regex['session'] = re.compile('.*(\d{4}-\d{2})', flags=re.IGNORECASE)
    # Description text has the company name and a description of the expense,
    # Separated either by a comma or semi-colon - we want to extract the company name
    # EG: AFC Energy; company developing alkaline fuel cell technology. Address: Unit 71.4 Dunsfold Park, Stovolds Hill, Cranleigh, Surrey, GU6 8TB. Undertake duties as Chair, run board meetings
    # ++> AFC Energy
    regex['company_name'] = re.compile('([a-z0-9\s\-]+)', flags=re.IGNORECASE)

    # Basic regex for extracting money value from a string - eg: £1,000
    # \xc2\xa3 = £ sign
    regex['money'] = re.compile(r".*?(\xc2\xa3(?:\s)?[0-9,\.\-]+)", flags=re.MULTILINE|re.DOTALL)

    regex['date'] = re.compile(r'.*?(?:Registered|Updated).*?([0-9]{1,2} [a-z]+ [0-9]{4})', flags=re.IGNORECASE|re.MULTILINE|re.DOTALL)

    # Extract payment amount and date registered
    # £5,000 on 15 August 2013.  Hours: 13 hrs. (Registered 22 August 2013)
    # => £5,000
    # => 22 August 2013
    # regex['payment'] = re.compile('.*£([0-9,.]+).*\(Registered ([a-z0-9 ]+)', flags=re.IGNORECASE)

    # List of interests type we're interested in
    # See http://www.publications.parliament.uk/pa/cm/cmregmem/1017/introduction.htm

    interest_types = {
        1: {
            'titles': ['Directorships', 'Remunerated directorships'],
            'model': DirectorshipModel
        },
        2: {
            'titles': ['Remunerated employment, office, profession'],
            'model': EmploymentModel
        },
        3: {
            'titles': ['Clients'],
            'model': ClientModel
        },
        4: {
            'titles': ['Sponsorships', 'Sponsorship or financial or material support'],
            'model': SponsorshipModel
        },
        5: {
            'titles': ['Gifts, benefits and hospitality'],
            'model': GiftModel
        },
        6: {
            'titles': ['Overseas visits'],
            'model': OverseesVisitModel
        },
        7: {
            'titles': ['Overseas benefits and gifts'],
            'model': OverseesGiftModel
        },
        8: {
            'titles': ['Land and property']
            # Land and property is given no numeric value, so we can not parse it out
        },
        9: {
            'titles': ['Registrable shareholdings', 'Shareholdings']
            # MPs do not declare a value against shareholdings - skipped
        },
        10: {
            'titles': ['Loans and other controlled transactions'],
            'model': LoanModel
        },
        11: {
            'titles': ['Miscellaneous']
            # Don't contain a value field
        }
    }

    # Placeholder dictionaries for the processed entry
    entry = {}
    donation = {}

    def __init__(self, *args, **kwargs):

        super(FinancialInterestsTask, self).__init__(*args, **kwargs)

        self.missing_mps = []

        # Create a list of missing MP names
        # But financial interests expect them to be in the format surname_firstname

        for mp_name in list_missing_mp_names():
            firstname, surname = mp_name.lower().split(' ')
            self.missing_mps.append('%s_%s' % (surname, firstname))

    def run(self):

        for session, register_url in self.registers:

            # If we have specified a particular session, skip all others
            if self.session and self.session != session:
                continue

            # Flag for whether we've matched an MP
            mp_processed = False

            for url in self.get_register_mp_urls(register_url):

                mp_identifier = self.get_mp_identifier_from_url(url)

                if self.mp and self.mp != mp_identifier:
                    continue

                mp_processed = True
                log.info('Processing MP %s for session %s', mp_identifier, session)
                self.process_mp_register(url, mp_identifier, session)

            if self.mp and not mp_processed:
                raise Exception('No MP found for %s' % self.mp)

            self.db_session.commit()

    @property
    def registers(self):
        """
        MP interests are organised on publications.parliament.uk so that each session/session
        Has it's own page of MP expenses. Fur the current session, there are reports for each month,
        And a main one for the whole session which is updated monthly
        See - http://www.publications.parliament.uk/pa/cm/cmregmem.htm
        This method returns a list of register pages for each of the sessions
        The home register page has broken HTML, so rather than try and fix it, I just generate a list

        @return: list of URLs
        """

        for session, i in [('2014-15', 911), ('2013-14', 1017), ('2012-13', 925), ('2011-12', 1782), ('2010-11', 100927)]:
            yield session, os.path.join('http://www.publications.parliament.uk/pa/cm/cmregmem', str(i), 'part1contents.htm')

    @staticmethod
    def get_register_mp_urls(register_url):
        """
        Generator returning list of MPs (and URLs) for a sessionly session page
        @param url:
        @return:
        """
        base_url = os.path.split(register_url)[0]
        soup = get_soup(register_url)

        links = soup.find_all('a')

        for link in links:
            try:
                if '_' in link.get("href"):
                    yield os.path.join(base_url, link.get("href"))

            except AttributeError:
                # If we cannot parse the MP Name, Skip the link
                # It is not a valid mp url
                continue
            except TypeError:
                continue

    @staticmethod
    def get_mp_identifier_from_url(url):
        """
        The URLs are structure like: http://www.publications.parliament.uk/pa/cm/cmregmem/911/balls_ed.htm
        So contain a better MP Identifier than the page title
        This extracts the MP name

        @param register_url:
        @return:
        """
        mp_identifier = url.split('/')[-1].replace('.htm', '')

        # Strip out the honorifics
        for honorific in ['rt-hon-', 'rt-hon', 'sir-', 'dame-', 'dr-', 'mrs-', 'hon-', '-junior']:
            mp_identifier = mp_identifier.replace(honorific, '')

        return mp_identifier

    @staticmethod
    def get_member_id(mp_identifier):
        """
        Get the member ID for the financial interest
        @param mp_identifier:
        @return:
        """

        try:
            member_id = FINANCIAL_INTEREST_IDS[mp_identifier]
        except KeyError:

            # Regex to get the first name and last name - and discard all else
            # smith_angela-c => smith, angela
            m = re.search(r'([a-z]+)_([a-z]+)', mp_identifier)

            surname = m.group(1)
            firstname = m.group(2)

            member_id = get_member_by_name(surname, firstname)

        return member_id

    def process_mp_register(self, url, mp_identifier, session):
        """
        Parse an individual page for an MP and save the data to mongo db

        @param url:
        @return:
        """
        interest_type_code = None
        sponsorship_type_b = False

        soup = get_soup(url)

        member_id = self.get_member_id(mp_identifier)

        # Check we have the member_id or if not it's one of the MPs we know about
        if not member_id:
            if mp_identifier in self.missing_mps:
                return
            else:
                raise Exception('No MP ID %s' % mp_identifier)

        # Position of session header changes in 10-11
        if session == '2010-11':
            session_text = soup.find(id='content-small').find('strong').getText()
        else:
            session_text = soup.find(id='titleBlockLinks').find('strong').getText()

        # Get the session session
        parsed_session = self.regex['session'].match(session_text).group(1)

        # Make sure it matches the session we think it is
        try:
            assert parsed_session == session, 'session mismatch %s' % parsed_session
        except AssertionError:
            # Date are wrong for the 2011-12 session
            if not (session == '2011-12' and parsed_session == '2010-12'):
                raise

        # Start by finding the page h2
        n = soup.find('h2')

        # Loop through each row
        # the indentation denotes the type of row
        while True:
            n = n.find_next_sibling()

            if not n:
                break

            line = n.getText().strip()

            # No entries for this MP in this session
            if line == 'Nil.' or line == 'Nil':
                log.info('Nil entries for %s: %s', mp_identifier, session)
                break

            # Regex checking the title for any of the known values eg: 1\. Remunerated directorships|2\. Remunerated employment ...
            # Id have this checking h3 tags, but the html is too badly formed
            # regex_interest_type = r"(%s)" % '|'.join([('%s\. %s') % (x, y[0]) for x, y in self.interest_types.items()])

            titles = []

            for key, interest_type in self.interest_types.items():
                for title in interest_type['titles']:
                    titles.append('%s\..*?%s' % (key, title))

            regex_interest_type = r"(%s)" % '|'.join(titles)

            if line:

                # Try and match the interest type line
                try:
                    match = re.search(regex_interest_type, line, re.IGNORECASE|re.MULTILINE|re.DOTALL).group(1)
                except AttributeError:

                    # If we have an error extracting header, add it to the error log
                    # These should all be bad formatting and can be ignored
                    if self.is_group_header(n):
                        log.error('%s Could not extract group: %s' % (mp_identifier, line))

                else:

                    # As we've swapped to another interest type group, make sure we commit the
                    # last entry, if we have one
                    if self.entry:
                        self._save_entry(session, member_id, mp_identifier, interest_type_code)

                    # Get the interest type code
                    interest_type_code = int(re.search('(\d{1,2})', match, re.IGNORECASE).group(1))

                    # If we've got to here, this is an interest type line so no
                    # further processing is necessary - continue to next line
                    continue

            # If we don't have an interest type code yet, continue
            if not interest_type_code:
                continue

            # If we have an interest type code parameter specified, continue until it's found
            if self.interest_type and self.interest_type != interest_type_code:
                continue

            # If output as is set, this is an interest type we're interested in
            if 'model' in self.interest_types[interest_type_code]:

                # We want to handle sponsorships differently
                if self.interest_types[interest_type_code]['model'] == SponsorshipModel:

                    # Sponsorships come in two parts
                    # (a) Donations to my constituency party or association - these we want to skip
                    # (b) Support in the capacity as an MP - these we want to include
                    if '(b)' in line:
                        sponsorship_type_b = True

                    # Sponsorship type A are party donations
                    # So until sponsorship type B section is reached, mark all
                    # Sponsorship entries as party donations
                    party_donation = False if sponsorship_type_b else True

                    # Caroline lucas has added party donations into type B
                    # Manually fix it here

                    if mp_identifier == 'lucas_caroline':
                        party_donation = True

                    self.process_donation_line(line, member_id, mp_identifier, interest_type_code, session, party_donation)

                elif self.interest_types[interest_type_code]['model'] in [GiftModel, OverseesGiftModel, OverseesVisitModel, LoanModel]:
                    self.process_donation_line(line, member_id, mp_identifier, interest_type_code, session)

                # Not sponsorship - normal entry
                else:
                    self.process_default_line(n, line, member_id, mp_identifier, interest_type_code, session)

        # Finished processing the page, so save the entry, if we have one
        if self.entry:
            self._save_entry(session, member_id, mp_identifier, interest_type_code)


    def process_default_line(self, n, line, member_id, mp_identifier, interest_type_code, session):

        # Get the html class
        cls = n.get('class') or []

        # Extract the vars from the line
        vars = {}
        try:
            # Entries can be x times £, total £
            # So we always want to select the last entry
            vars['value'] = self.currency_to_float(self.regex['money'].findall(line)[-1])
        except IndexError:
            pass

        try:
            vars['date'] = self.regex['date'].match(line).group(1)
        except AttributeError:
            pass

        # Has this been donated to charity
        if 'charity' in line and ('donated' or 'donation' or 'paid') in line:
            vars['donated_to_charity'] = True

        if 'indent' in cls:

            # Merge the vars into the main entry.
            # If we didn't manage to extract a value or date, nothing will get overwritten
            # So we can have values coming from multiple lines
            self.entry.update(vars)

            # Do not overwrite description if it's entry
            # Sometimes the registered date etc., are in subsequent lines
            if not 'description' in self.entry:
                self.entry['description'] = line

        # This is a sub entry item
        elif 'indent2' in cls or 'indent3' in cls:

            # Ensure subentries list exists
            try:
                self.entry['sub_entries']
            except KeyError:
                self.entry['sub_entries'] = list()

            # If we do not have either a date or value extracted from the sub entry line
            # Ignore it - there's a load of cruft stored here
            if 'date' not in vars and 'value' not in vars:
                return

            vars['description'] = line

            # We're getting a few where subentries are split into two rows
            # So if we have date only one row, value only the next (abd visa versa) merge them together
            # We only want to do this if we have more than one subentry - this isn't a new entry
            if ('date' not in vars or 'value' not in vars) and len(self.entry['sub_entries']) > 0:

                sub_entry_key = len(self.entry['sub_entries']) - 1
                previous_subentry = self.entry['sub_entries'][sub_entry_key]

                # If the difference between this and the previous sub entry is date and value
                # So one has date, one has value, lets merge them together
                if set(previous_subentry.keys()).symmetric_difference(set(vars.keys())) == set(['value', 'date']):
                    # Lets keep the first description
                    del vars['description']
                    # Add the new vars to the previous subentry item
                    self.entry['sub_entries'][sub_entry_key].update(vars)

                    # And skip to next line
                    return

            self.entry['sub_entries'].append(vars)

        # If this is an empty line, commit the entry
        # Or if this has class prevNext (the links at the bottom) commit
        if not line or 'prevNext' in cls:
            # Add the entry - still need to check as we can have sections starting with an empty line
            if self.entry:
                self._save_entry(session, member_id, mp_identifier, interest_type_code)
                # And reset the entry object
                self.entry = {}

    def process_donation_line(self, line, member_id, mp_identifier, interest_type_code, session, party_donation=False):
        """
        Process a donation style line
        Used for spn

        Loop through each line, extracting name of donor and amount
        When we get to Date, commit changes and raise Exception if one of the values
        Is not null
        After commit, reset vars to None
        EG:
        Name of donor: Unite the Union
        Address of donor: Unite House, 128 Theobald’s Road, Holborn WC1X 8TN
        Amount of donation or nature and value if donation in kind: £3,000
        Donor status: trade union
        (Registered 3 April 2014)

        @return:
        """

        # If this is a loan type, we want to use slightly different row formatters
        # But the rest statys the same
        if interest_type_code == 10:

            rows = OrderedDict([
                ('name', r'Name of lender(?:s?)\s?:(.*)'),
                ('address', r'Address of donor(?:s?)\s?:(.*)'),
                ('value', r'Amount of(?:.*?)(\xc2\xa3(?:.*?)[0-9,\.]+)'),
                ('date', r"\((Registered)"),  # We want this to trigger saving the entry
            ])

            description = 'Lender'

        else:

            rows = OrderedDict([
                ('name', r'Name of donor(?:s?)\s?:(.*)'),
                ('address', r'Address of donor(?:s?)\s?:(.*)'),
                ('value', r'Amount of donation(?:.*?)(\xc2\xa3(?:.*?)[0-9,\.]+)'),
                ('date', r"\((Registered)"),  # We want this to trigger saving the entry
            ])

            description = 'Donor'

        # Has this been donated to charity
        if 'charity' in line and ('donated' or 'donation' or 'paid') in line:
            self.donation['donated_to_charity'] = True

        for row, regex in rows.items():
            try:
                self.donation[row] = re.search(regex, line, re.IGNORECASE | re.MULTILINE | re.DOTALL).group(1).strip()
            except AttributeError:
                pass
            else:

                if row == 'value':

                    # Do we have multiple values?
                    values = re.findall(r'(\xc2\xa3(?:.*?)[0-9,\.]+)', line, re.IGNORECASE | re.MULTILINE | re.DOTALL)

                    if len(values) > 1:
                        self.donation[row] = values[-1]
                        log.info('Multiple values for line. Assuming last is total.')

                    # Payment amount - need to parse currency to int
                    self.donation[row] = self.currency_to_float(self.donation[row])

                # Donation date is the last line - add as payment and reset vars so we get error if not found
                # In subsequent groups
                if row == 'date':
                    # So we always submit, date property just contains "registered"
                    # so delete this property, and extract the proper date from the line
                    del self.donation[row]

                    # So try and extract the proper date
                    date_regex = r"(\d{1,2}(?:\s+)?(?:%s)(?:\s+)?\d{4})" % '|'.join(calendar.month_name[1:])
                    try:
                        self.donation['date'] = re.search(date_regex, line, re.IGNORECASE | re.MULTILINE | re.DOTALL).group(1).strip()
                    except AttributeError:
                        pass

                    if 'address' in self.donation:
                        # If we have the address but not the name, just use the address as the name
                        if 'name' not in self.donation:
                            self.donation['name'] = self.donation['address']

                        del self.donation['address']

                    # Replace any known errors
                    self.donation = self.replace_known_errors(mp_identifier, self.donation)

                    missing_fields = []

                    # Are any of the core fields missing? (We do not care about address)
                    for required_field in ['name', 'value', 'date']:
                        if required_field not in self.donation:
                            missing_fields.append(required_field)

                    if missing_fields:

                        err = '%s. Missing donation fields - %s', mp_identifier, ','.join(missing_fields)

                        # If we have a value for this donation, it's worth investigating further
                        # so raise an exception
                        if 'value' in self.donation:

                            # David laws has organised his so there is a total,
                            # followed by individual entries - so do not raise exception
                            # for the total entry
                            if mp_identifier == 'laws_david' and self.donation['value'] == 49600.0:
                                continue
                            # Glen john has declared an intern - skip it
                            elif mp_identifier == 'glen_john' and session == '2011-12' and self.donation['value'] == 5500.0:
                                continue


                            print self.donation
                            raise Exception(err)
                        else:
                            # Otherwise just log a warning
                            log.warning(err)
                    else:

                        # Insert it into the database
                        self._db_insert(interest_type_code,
                                        session=session,
                                        member_id=member_id,
                                        value=self.donation['value'],
                                        date=self.donation['date'],
                                        description='%s: %s' % (description, self.donation['name']),  # Not every sub entry has a proceeding row
                                        donated_to_charity=self.donation['donated_to_charity'] if 'donated_to_charity'in self.donation else False,
                                        party_donation=party_donation
                        )

                    # Reset self.donation ready for the next rows
                    self.donation = {}





    def _db_insert(self, interest_type_code, **kwargs):
        # Get the class
        cls = self.interest_types[interest_type_code]['model']
        self.db_session.add(cls(**kwargs))

    def _save_entry(self, session, member_id, mp_identifier, interest_type_code):

        def _date_or_default(entry):
            """
            If we're only missing a date, add a default one at the start of the year
            """
            try:
                return entry['date']
            except KeyError:
                return '1 January 20%s' % session.split('-')[1]

        if not member_id:
            print 'NO MEMBER ID'
            print self.entry
            raise Exception

        if 'sub_entries' in self.entry:

            for sub_entry in self.entry['sub_entries']:

                sub_entry = self.replace_known_errors(mp_identifier, sub_entry)

                try:
                    donated_to_charity = sub_entry['donated_to_charity'] or self.entry['donated_to_charity']
                except KeyError:
                    donated_to_charity = False

                # If we don't have a subentry date, but we do have a tertiary entry date, then use that instead
                if 'date' not in sub_entry and 'date' in self.entry:
                    sub_entry['date'] = self.entry['date']

                try:

                    self._db_insert(interest_type_code,
                                    session=session,
                                    member_id=member_id,
                                    value=sub_entry['value'],
                                    date=_date_or_default(sub_entry),
                                    description=self.entry['description'] if 'description' in self.entry else None,  # Not every sub entry has a proceeding row
                                    sub_entry=sub_entry['description'],
                                    donated_to_charity=donated_to_charity
                    )

                except KeyError, e:
                     # If we have a value, raise an exception for further investigation
                    if 'value' in sub_entry:
                        raise Exception('Missing subentry data, but we do have value.')
                    else:
                        log.warning('%s: Missing payment data %s: %s', mp_identifier, e, sub_entry)

        else:

            self.entry = self.replace_known_errors(mp_identifier, self.entry)

            try:

                try:
                    donated_to_charity = self.entry['donated_to_charity']
                except KeyError:
                    donated_to_charity = False

                self._db_insert(interest_type_code,
                                session=session,
                                member_id=member_id,
                                value=self.entry['value'],
                                date=_date_or_default(self.entry),
                                description=self.entry['description'],
                                donated_to_charity=donated_to_charity
                )

            except KeyError, e:

                 # If we have a value, raise an exception for further investigation
                if 'value' in self.entry:
                    raise Exception('Missing entry data, but we do have value.')
                else:
                    log.warning('%s: Missing payment data %s: %s', mp_identifier, e, self.entry)

        # Reset the entry dict
        self.entry= {}

    def currency_to_float(self, currency_str):
        """
        Convert current string to int
        @param str: currency to convert
        @return: int
        """

        try:

            # Remove leading/trailing empty spaces
            currency_str = currency_str.strip()

            # If that last char is a full stop, remove it
            currency_str = currency_str.rstrip('.')

            # If the last char is a - remove it
            currency_str = currency_str.rstrip('-')

            # print currency_str

            # Common problem is adding extra decimal points, instead of thousands comma separator
            # SO if we have more than one decimal point, remove it
            point_count = currency_str.count('.')
            if point_count > 1:
                currency_str = currency_str.replace('.', '', point_count-1)

            # Some currency values have a range: e.g.: Spencer, Mark 20-14-15: £5-10,000
            # We want to make sure these aren't recorded as £5, so - is included in the regex
            # But we want to split on it and take the upper bounds
            if '-' in currency_str:
                currency_str = currency_str.split('-')[1]

            value = re.sub(r'[^\d.]', '', currency_str.replace(',', '').rstrip('.'))
            value = Decimal(value)
        except AttributeError:
            print 'Could not parse amount: ', currency_str
            raise
        finally:
            # print value
            return float(value)

    def is_group_header(self, n):
        """
        Each MP page is separated into groups:

            1. Directorships
            11. Miscellaneous

        Usually these are identifiable by a <h3> tag - but sometimes are just
        p tags with class = shd0

        """
        return n.name == 'h3' or 'shd0' in n.get('class', [])

    def replace_known_errors(self, mp_identifier, entry):

        """
        Replace any known errors
        @param mp_name:
        @param entry:
        @return:
        """
        entry_str = json.dumps(entry)
        try:
            corrected_entry = FINANCIAL_INTEREST_ERRORS[mp_identifier][entry_str]
        except KeyError:
            pass
        else:
            entry.update(corrected_entry)

        return entry


if __name__ == "__main__":
    luigi.run(main_task_cls=FinancialInterestsTask)