#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Boolean
from sqlalchemy.orm import relationship
from mp_data.model import Base, MemberModel

class CommonsQuestionModel(Base):

    # Early Day Motion

    __tablename__ = 'commons_question'

    id = Column(Integer, primary_key=True, nullable=False)

    # Type of bill - Early day motion etc.,
    type = Column(String, nullable=False)
    tabling_member = Column(Integer, ForeignKey(MemberModel.id, ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    question_text = Column(String)

    # Is this question about a registered interest - only for Q's
    registered_interest = Column(Boolean, default=False)

    # Polymorphic identity to allow for subclasses
    __mapper_args__ = {
        'polymorphic_on': type,
    }

class CommonsWrittenQuestionModel(CommonsQuestionModel):

    # Written question

    __mapper_args__ = {
        'polymorphic_identity': 'written_question'
    }

class CommonsOralQuestionModel(CommonsQuestionModel):

    # Oral question
    __mapper_args__ = {
        'polymorphic_identity': 'oral_question'
    }