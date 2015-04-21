#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from mp_data import config
from mp_data.model import Base

_engines = {}

_session = []

def _get_engine():

    connection_url = config.get('postgres', 'write_url')
    engine = _engines.get(connection_url)

    if not engine:
        engine = sqlalchemy.create_engine(connection_url)
        _engines[connection_url] = engine
    return engine

def get_session():

    if not _session:
        _session.append(sessionmaker(bind=_get_engine())())

    return _session[0]


def setup_db():

    engine = _get_engine()

    print 'Creating DB tables'
    Base.metadata.create_all(engine)

    print 'Creating DB views'
    conn = engine.connect()
    trans = conn.begin()
    # Open the sql file and execute against the connection
    f = os.path.join(os.path.dirname(__file__), 'sql', 'views.sql')
    with open(f, "r") as sql:
        conn.execute(sql.read())
        trans.commit()


if __name__ == '__main__':
    setup_db()
