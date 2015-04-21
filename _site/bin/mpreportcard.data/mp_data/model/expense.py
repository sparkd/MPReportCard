#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, ForeignKey
from mp_data.model import Base
from mp_data.model.member import MemberModel

class ExpenseModel(Base):

    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)

    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False, index=True)

    # Session - for example 14_15
    session = Column(String, nullable=False)
    mp = Column(String, nullable=False)

    date = Column(Date, nullable=False)
    value = Column(Numeric(scale=2), nullable=False)

    category = Column(String)
    description = Column(String)  # Expense type
    claim_number = Column(String)  # Some have claim number as "Payment to supplier" so we can't use the ID

