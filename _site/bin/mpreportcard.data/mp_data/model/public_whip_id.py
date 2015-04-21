#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, ForeignKey
from mp_data.model import Base, MemberModel


class PublicWhipIDModel(Base):

    # Public whip IDs linked to the main member ID

    __tablename__ = 'public_whip_id'

    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), primary_key=True, nullable=False)
    pw_id = Column(Integer, unique=True, nullable=False)