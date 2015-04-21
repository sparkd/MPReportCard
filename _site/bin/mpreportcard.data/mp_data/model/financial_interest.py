#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, Boolean, ForeignKey
from mp_data.model import Base
from mp_data.model.member import MemberModel

class FinancialInterestModel(Base):

    __tablename__ = 'financial_interests'

    id = Column(Integer, primary_key=True)

    member_id = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False)
    session = Column(String, nullable=False)

    date = Column(Date, nullable=False)
    value = Column(Numeric(scale=2), nullable=False)
    donated_to_charity = Column(Boolean, nullable=False)
    party_donation = Column(Boolean, nullable=False, default=False)
    description = Column(String)
    sub_entry = Column(String)
    type = Column(String, nullable=False)

    # Polymorphic identity to allow for subclasses
    __mapper_args__ = {
        'polymorphic_on': type,
    }


class EmploymentModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'employment'
    }


class SponsorshipModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'sponsorship'
    }

class GiftModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'gift'
    }

class OverseesVisitModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'oversees_visit'
    }

class OverseesGiftModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'oversees_gift'
    }


class ClientModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'client'
    }


class DirectorshipModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'directorship'
    }

class LoanModel(FinancialInterestModel):

    __mapper_args__ = {
        'polymorphic_identity': 'loan'
    }