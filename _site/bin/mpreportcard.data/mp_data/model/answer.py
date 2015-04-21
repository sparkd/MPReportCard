#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""


from sqlalchemy import Column, Integer, Boolean, ForeignKey, Date
from mp_data.model import Base
from mp_data.model.member import MemberModel

class AnswerModel(Base):

    """
    Debates - really basic, just need to sub member ID
    """

    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(Date, nullable=False)
    # Is this question about a registered interest - only for Q's
    registered_interest = Column(Boolean, default=False)
    # Speaker
    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False, index=True)