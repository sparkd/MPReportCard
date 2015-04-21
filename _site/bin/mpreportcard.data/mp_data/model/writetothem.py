#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Boolean
from sqlalchemy.orm import relationship
from mp_data.model import Base, MemberModel


class WriteToThemModel(Base):

    # Early Day Motion

    __tablename__ = 'writetothem'

    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), primary_key=True, nullable=False)
    year = Column(String, nullable=False)
    total_sent = Column(Integer, nullable=False, default=0)
    surveys = Column(Integer, nullable=False, default=0)
    replies = Column(Integer, nullable=False, default=0)
    data_quality_indicator = Column(String, nullable=False)