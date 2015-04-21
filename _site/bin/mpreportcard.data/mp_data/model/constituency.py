#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, String
from mp_data.model import Base

class ConstituencyModel(Base):

    __tablename__ = 'constituency'

    # Uses the ID from westminster postcodes
    # https://geoportal.statistics.gov.uk/geoportal/catalog/search/resource/details.page?uuid=%7B7FEF5398-737C-41F5-A250-600AEE209BDE%7D
    id = Column(String(length=9), primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    # TODO: KML Shape?
