#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import json
import shelve
from mp_data.db import get_session
from mp_data import config, MP_COUNT, ELECTION_DATE
from mp_data.model import *
from mp_data.lib.helpers import float_to_int, get_twfy_ids
from sqlalchemy import and_, func, cast, Integer
from sqlalchemy.orm.exc import NoResultFound
from collections import OrderedDict

db_session = get_session()

def get_party_name(name):
    """
    Get party name, converting to a shortened name if we have one
    :param name:
    :return:
    """

    shortnames = {
        'Scottish National': 'SNP',
        'Democratic Unionist': 'DUP',
        'Social Democratic & Labour Party': 'SDLP',
        'Liberal Democrat': 'Lib Dem',
        'UK Independence Party': 'UKIP'
    }

    try:
        party = shortnames[name]
    except KeyError:
        party = name

    return party


def main():
    """
    Generate data for the website

    Caches MP data in a shelf - delete /tmp/mp.shelf to re build

    @return:
    """

    outfile = os.path.join(config.get('data', 'output_dir'), 'data.js')
    data = []
    averages = {}

    mp_count = db_session.query(MemberModel).count()

    # Make sure we have 650 MPS
    assert mp_count == MP_COUNT

    # Get count of GOVT ministers
    ministers_count = db_session.query(MemberModel).join(PostModel).filter(PostModel.type == 'government').count()

    edms_ids = {}

    # Get member ID to EDMS ID mapping
    for member_id, edms_id in db_session.query(EDMSModel.member_id, EDMSModel.edms_id).distinct():
        edms_ids[member_id] = edms_id

    # Get member ID to EDMS ID mapping
    for member_id, edms_id in db_session.query(EDMSModel.member_id, EDMSModel.edms_id).distinct():
        edms_ids[member_id] = edms_id


    mps = db_session.query(MemberModel).join(ConstituencyModel).join(PublicWhipIDModel).values(
        MemberModel.id,
        MemberModel.name,
        MemberModel.list_name,
        MemberModel.start_date,
        MemberModel.party,
        ConstituencyModel.name.label("constituency"),
        PublicWhipIDModel.pw_id
    )

    print 'Retrieving MPS'
    shelf = shelve.open('/tmp/mp.shelf')

    try:
        data = shelf['mp']
        print 'WARNING: Retrieving MP data from cache'
    except KeyError:

        for mp in mps:
            item = mp._asdict()

            # Get party short name
            item['party_short'] = get_party_name(mp.party)

            # Add the EDMS ID
            try:
                item['edms_id'] = edms_ids[mp.id]
            except KeyError:
                # To be expected: govt ministers etc., do not submit EDMS
                pass

            # UKIP MPs have a start date from when they joined UKIP
            # Reset to start of parliament so stats are correct
            if mp.id in [4049, 1527]:
                mp.start_date = ELECTION_DATE

            # Get the votes
            item.update(get_votes(mp.id, mp.start_date))

            # Get replies
            item.update(get_replies(mp.id))

            # Posts
            item.update(get_posts(mp.id))

            item['expenses'] = get_expenses(mp.id)
            item['interests'] = get_interests(mp.id)
            item['answers'] = get_answers(mp.id)
            item['debates'] = get_debates(mp.id)
            item['speeches'] = get_speeches(mp.id)
            item['edms'] = get_edms(mp.id)
            item['rebel_votes'] = get_rebel_votes(mp.id)

            if len(data) and (len(data) % 10 == 0):
                print "\t{0:.0f}%".format(float(len(data)) / MP_COUNT * 100)

            # We don't use the start date - remove it
            del item['start_date']

            data.append(item)

        shelf['mp'] = data
        shelf.close()

    print 'Retrieving averages'

    ## Get totals/averages

    # Get expenses average - it's better to do this here rather than in the front end
    # as otherwise we'll get rounding issues
    total_interests = db_session.query(func.sum(FinancialInterestModel.value)).filter(FinancialInterestModel.party_donation == False).scalar()
    averages['interests'] = float_to_int(total_interests / mp_count)

    total_expenses = db_session.query(func.sum(ExpenseModel.value)).scalar()
    averages['expenses'] = float_to_int(total_expenses / mp_count)

    averages['answers'] = db_session.query(AnswerModel).count() / mp_count
    averages['debates'] = db_session.query(DebateModel.debate_id).distinct().count() / mp_count

    averages['edms'] = db_session.query(func.sum(EDMSModel.number_of_signatures)).scalar() / (mp_count - ministers_count)

    # Votes average - use items as it's calculated based on possible attended
    averages['votes_percentage'] = float_to_int(sum(float(i['votes_percentage']) for i in data) / mp_count)

    # Rebel votes average
    averages['rebel_votes'] = float_to_int(db_session.execute('SELECT SUM(rebel_votes) FROM _rebel_votes').scalar() / mp_count)

    # We want to exclude the MPs who don't accept letters via they write to you etc.,
    # When calculating the percentage
    writetothem_mp_count = db_session.query(WriteToThemModel).filter(WriteToThemModel.data_quality_indicator == 'good').count()
    averages['replies_percentage'] = float_to_int(sum(float(i['replies_percentage']) for i in data if 'replies_percentage' in i) / writetothem_mp_count)

    print 'Retrieving party stats'
    stats_data = get_stats_data()

    # Create an empty list for both votes and replies
    # And populate every party with 0.
    # We can then make sure if we have no data, the value is still 0
    votes = {}
    replies = {}
    replies_counter = {}
    for party in stats_data['party_members'].keys():
        votes[party] = 0
        replies[party] = 0
        # Count of number of members who have replies
        replies_counter[party] = 0

    # Votes and replies are better calculated looping through the mps
    for mp in data:

        party = get_party_name(mp['party'])

        if party == 'Speaker':
            continue

        votes[party] += float(mp['votes_percentage'])
        if mp['data_quality_indicator'] == 'good':
            replies[party] += int(mp['replies_percentage'])
            replies_counter[party] += 1


    # Add averages to the the stats data
    stats_data['votes'] = {}
    # Average out the votes
    for party, total in votes.items():
        stats_data['votes'][party] = round(total / stats_data['party_members'][party], 1)

    stats_data['replies'] = {}
    # Average out the replies - we do not have data on every MP, so need
    # to average only on those who we have data on
    for party, total in replies.items():
        if total:
            stats_data['replies'][party] = total / replies_counter[party]


    # Tidy up the stats data - make sure we have data for every party and
    # all parties are in the same order

    all_parties = stats_data['party_members'].keys()

    # Ensure we have a value for all parties
    for k in stats_data.keys():

        if k == 'govt_posts':
            continue

        for party in all_parties:
            try:
                stats_data[k][party]
            except KeyError:
                print 'Warning: Missing party %s in %s' % (party, k)
                stats_data[k][party] = 0

        # And sort
        stats_data[k] = OrderedDict(sorted(stats_data[k].items()))

    print 'Writing data'

    with open(outfile, 'w') as outfile:
        outfile.write('var members_data = ')
        json.dump(data, outfile)
        outfile.write('\n')
        outfile.write('var averages_data = ')
        json.dump(averages, outfile)
        outfile.write('\n')
        outfile.write('var stats_data = ')
        json.dump(stats_data, outfile)


def get_stats_data():

    def map_data_dict(result):
        return {get_party_name(r.party): r.value for r in result}

    stats = {}

    # Get party stats, so averages can be calculated
    party_members = db_session.query(MemberModel.party, func.count(MemberModel.id).label("value")).filter(MemberModel.party != 'Speaker').group_by(MemberModel.party).order_by(MemberModel.party).all()
    stats['party_members'] = map_data_dict(party_members)

    stats['financial_interests'] = map_data_dict(
        db_session.query(MemberModel.party, cast(func.round(func.sum(FinancialInterestModel.value)), Integer).label("value")).join(FinancialInterestModel).filter(
            and_(MemberModel.party != 'Speaker', FinancialInterestModel.party_donation == False)).group_by(MemberModel.party).order_by(MemberModel.party).all())

    stats['expenses'] = map_data_dict(
        db_session.query(MemberModel.party, cast(func.round(func.sum(ExpenseModel.value)), Integer).label("value")).join(ExpenseModel).filter(MemberModel.party != 'Speaker').group_by(
            MemberModel.party).order_by(MemberModel.party).all())

    # Debates
    debates = db_session.query(MemberModel.party, func.count(DebateModel.debate_id).label("value")).join(DebateModel).filter(MemberModel.party != 'Speaker').group_by(MemberModel.party).order_by(MemberModel.party).all()
    stats['debates'] = map_data_dict(debates)

    answers = db_session.query(MemberModel.party, func.count(AnswerModel.id).label("value")).join(AnswerModel).filter(MemberModel.party != 'Speaker').group_by(MemberModel.party).order_by(MemberModel.party).all()
    stats['answers'] = map_data_dict(answers)

    edms = db_session.query(MemberModel.party, func.sum(EDMSModel.number_of_signatures).label("value")).join(EDMSModel).filter(MemberModel.party != 'Speaker').group_by(MemberModel.party).order_by(MemberModel.party).all()
    stats['edms'] = map_data_dict(edms)

    rebel_votes = db_session.execute('SELECT m.party, sum(rebel_votes)::int as value from members m inner join _rebel_votes rv ON rv.member_id = m.id GROUP BY m.party ORDER BY party')
    stats['rebel_votes'] = map_data_dict(rebel_votes)

    edms = db_session.query(MemberModel.party, func.sum(EDMSModel.number_of_signatures).label("value")).join(EDMSModel).filter(MemberModel.party != 'Speaker').group_by(MemberModel.party).order_by(MemberModel.party).all()
    stats['edms'] = map_data_dict(edms)

    # To calculate averages correctly for EDMS and answers, we need to know how many lib dem , cons are in govt posts
    # select m.party, count(distinct(m.id)) from members m inner join posts p on p.member_id = m.id where type = 'government' group by party;
    govt_posts = db_session.execute("select m.party, count(distinct(m.id)) as value from members m inner join posts p on p.member_id = m.id where type = 'government' group by party")
    stats['govt_posts'] = map_data_dict(govt_posts)

    return stats


def get_expenses(member_id):
    expenses = db_session.query(func.sum(ExpenseModel.value)).filter(ExpenseModel.member_id == member_id).scalar()
    if expenses:
        return float_to_int(expenses)
    else:
        return 0


def get_interests(member_id):
    financial_interests = db_session.query(func.sum(FinancialInterestModel.value)).filter(and_(FinancialInterestModel.member_id == member_id, FinancialInterestModel.party_donation == False)).scalar()
    if financial_interests:
        return float_to_int(financial_interests)
    else:
        return 0


def get_answers(member_id):
    return db_session.query(AnswerModel).filter(AnswerModel.member_id == member_id).count()


def get_debates(member_id):
    """
    The number of debates an MP has spoken at
    :param member_id:
    :return:
    """
    return db_session.query(DebateModel.debate_id).distinct().filter(DebateModel.member_id == member_id).count()


def get_speeches(member_id):
    """
    Number of times a member has spoken
    :param member_id:
    :return:
    """
    return db_session.query(DebateModel).filter(DebateModel.member_id == member_id).count()

def get_edms(member_id):
    edms_sum = db_session.query(func.sum(EDMSModel.number_of_signatures)).filter(EDMSModel.member_id == member_id).scalar()
    return edms_sum or 0

def get_rebel_votes(member_id):
    return db_session.execute('SELECT rebel_votes FROM _rebel_votes WHERE member_id = %s' % member_id).scalar()


def get_replies(member_id):
    try:
        write_to_them = db_session.query(WriteToThemModel.replies, WriteToThemModel.surveys, WriteToThemModel.data_quality_indicator).filter(WriteToThemModel.member_id == member_id).one()
    except NoResultFound:
        return {
            'replies_percentage': 0,
            'data_quality_indicator': False
        }
    else:
        replies = write_to_them._asdict()

        if write_to_them.replies and write_to_them.surveys:
            replies['replies_percentage'] = float_to_int((float(write_to_them.replies) / float(write_to_them.surveys)) * 100)
        else:
            replies['replies_percentage'] = 0

        return replies


def get_votes(member_id, start_date):
    """
    This need to return a percentage of votes attended out of all
    possible (since MP start date)
    :return:
    """
    votes = dict()
    votes['votes_possible'] = db_session.query(VotesModel).filter(VotesModel.date > str(start_date)).count()
    votes['votes_attended'] = db_session.query(MembersVotesModel).join(VotesModel).filter(and_(MembersVotesModel.member_id == member_id, VotesModel.date > str(start_date))).count()
    votes['votes_percentage'] = "%.1f" % ((float(votes['votes_attended']) / float(votes['votes_possible'])) * 100);
    return votes

def get_posts(member_id):

    ret = dict(
        post=None,
        govt=False
    )

    try:
        # Retrieve the latest post for this member - and prefer govt posts over parliamentary
        post = db_session.query(PostModel).filter(PostModel.member_id == member_id).order_by(PostModel.type, PostModel.start_date).limit(1).one()
    except NoResultFound:
        pass
    else:
        ret['post'] = post.title

        # As we have posts for this member, check if they hold a government position
        govt = db_session.query(PostModel).filter(and_(PostModel.member_id == member_id, PostModel.type == 'government')).count()
        if govt:
            ret['govt'] = True

    return ret


if __name__ == '__main__':
    main()

