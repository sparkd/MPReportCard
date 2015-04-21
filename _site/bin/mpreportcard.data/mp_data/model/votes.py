#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint
from mp_data.model import Base
from mp_data.model.member import MemberModel

class VotesModel(Base):

    # Commons votes

    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True, nullable=False)

    session_id = Column(Integer, nullable=False)  # Public Whip ID
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)

    # PWID is unique for each session
    UniqueConstraint('session_id', 'date')


class MembersVotesModel(Base):

    """
    Members votes
    """

    __tablename__ = 'members_votes'

    id = Column(Integer, primary_key=True, nullable=False)
    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False, index=True)
    vote_id = Column(Integer, ForeignKey(VotesModel.id, ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False, index=True)
    voted = Column(String, nullable=False)
    result = Column(String, nullable=False)