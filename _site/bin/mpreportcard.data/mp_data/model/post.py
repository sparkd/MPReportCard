#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, ForeignKey, String, Date, Boolean, Enum
from mp_data.model import Base
from mp_data.model.member import MemberModel

class PostModel(Base):

    # Early Day Motion

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    type = Column(Enum('government', 'opposition', 'parliamentary', name='post_type'))
