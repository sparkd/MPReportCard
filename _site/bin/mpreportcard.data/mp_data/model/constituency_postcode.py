#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, String, ForeignKey
from mp_data.model import Base
from mp_data.model.constituency import ConstituencyModel

class ConstituencyPostcodeModel(Base):

    # Constituency postcodes

    __tablename__ = 'constituency_postcode'

    constituency_id = Column(String(length=9), ForeignKey(ConstituencyModel.id, ondelete="CASCADE"), primary_key=True, nullable=False)
    postcode = Column(String(length=7), primary_key=True, nullable=False)
