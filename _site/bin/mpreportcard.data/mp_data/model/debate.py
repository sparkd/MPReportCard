#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""


from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint
from mp_data.model import Base
from mp_data.model.member import MemberModel

class DebateModel(Base):

    """
    Debates - really basic, just need to sub member ID
    """

    __tablename__ = 'debates'

    id = Column(Integer, primary_key=True, nullable=False)
    debate_id = Column(String)
    date = Column(Date, nullable=False)
    # Speaker
    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False, index=True)
