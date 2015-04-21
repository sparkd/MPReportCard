#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, Boolean, Enum, ForeignKey
from mp_data.model import Base
from mp_data.model.constituency import ConstituencyModel

class MemberModel(Base):

    # Early Day Motion

    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, nullable=False)
    # Pims_Id matches EDMI ID on http://www.edms.org.uk
    pims_id = Column(Integer, unique=True, nullable=False)
    dods_id = Column(Integer, unique=True, nullable=False)

    name = Column(String, nullable=False)

    # Useful for joining with financial interests?
    list_name = Column(String, nullable=False)

    # Link to constituency table
    constituency_id = Column(String(length=9), ForeignKey(ConstituencyModel.id, ondelete="CASCADE"), unique=True, nullable=False)

    party = Column(String)
    gender = Column(Enum('M', 'F', name='gender'))
    standing_down = Column(Boolean, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    number_committees = Column(Integer)
    twitter = Column(String)
    website = Column(String)