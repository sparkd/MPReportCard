#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Boolean
from sqlalchemy.orm import relationship
from mp_data.model import Base, MemberModel


class EDMSModel(Base):

    # Early Day Motion

    __tablename__ = 'edms'

    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), primary_key=True, nullable=False)
    # 14-15 etc.,
    session = Column(String, primary_key=True, nullable=False)
    number_of_signatures = Column(Integer)
    edms_id = Column(Integer)