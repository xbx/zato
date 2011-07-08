# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps

# SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, \
     ForeignKey, Sequence, Boolean, LargeBinary, UniqueConstraint, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

# Zato
from zato.common.util import make_repr, object_attrs

__all__ = ["Base", "Cluster", "Server", "WSSDefinition", "WSSDefinitionPassword",
           "SQLConnectionPool", "ZatoInstallState"]

Base = declarative_base()

################################################################################

def to_json(model):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    json = {}
    json["fields"] = {}
    json["pk"] = getattr(model, "id")

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json["fields"][col.name] = getattr(model, col.name)

    return dumps([json])

class ZatoInstallState(Base):
    """ Contains a row for each Zato installation belonging to that particular
    ODB. For instance, installing Zato 1.0 will add a new row, installing 1.1
    will create a new one, and so on.
    """
    __tablename__ = "install_state"

    id = Column(Integer,  Sequence("install_state_seq"), primary_key=True)
    version = Column(String(200), unique=True, nullable=False)
    install_time = Column(DateTime(), nullable=False)
    source_host = Column(String(200), nullable=False)
    source_user = Column(String(200), nullable=False)

    def __init__(self, id=None, version=None, install_time=None, source_host=None,
                 source_user=None):
        self.id = id
        self.version = version
        self.install_time = install_time
        self.source_host = source_host
        self.source_user = source_user

class Cluster(Base):
    """ Represents a Zato cluster.
    """
    __tablename__ = "cluster"

    id = Column(Integer,  Sequence("cluster_id_seq"), primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    odb_type = Column(String(30), nullable=False)
    odb_host = Column(String(200), nullable=False)
    odb_port = Column(Integer(), nullable=False)
    odb_user = Column(String(200), nullable=False)
    odb_db_name = Column(String(200), nullable=False)
    odb_schema = Column(String(200), nullable=True)
    amqp_host = Column(String(200), nullable=False)
    amqp_port = Column(Integer(), nullable=False)
    amqp_user = Column(String(200), nullable=False)
    lb_host = Column(String(200), nullable=False)
    lb_agent_port = Column(Integer(), nullable=False)
    sec_server_host = Column(String(200), nullable=False)
    sec_server_port = Column(Integer(), nullable=False)

    def __init__(self, id=None, name=None, description=None, odb_type=None,
                 odb_host=None, odb_port=None, odb_user=None, odb_db_name=None,
                 odb_schema=None, amqp_host=None, amqp_port=None,
                 amqp_user=None, lb_host=None, lb_agent_port=None,
                 sec_server_host=None, sec_server_port=None):
        self.id = id
        self.name = name
        self.description = description
        self.odb_type = odb_type
        self.odb_host = odb_host
        self.odb_port = odb_port
        self.odb_user = odb_user
        self.odb_db_name = odb_db_name
        self.odb_schema = odb_schema
        self.amqp_host = amqp_host
        self.amqp_port = amqp_port
        self.amqp_user = amqp_user
        self.lb_host = lb_host
        self.lb_agent_port = lb_agent_port
        self.sec_server_host = sec_server_host
        self.sec_server_port = sec_server_port

    def __repr__(self):
        return make_repr(self)

    def to_json(self):
        return to_json(self)

class Server(Base):
    """ Represents a Zato server.
    """
    __tablename__ = 'server'
    __table_args__ = (UniqueConstraint('name'), {})

    id = Column(Integer,  Sequence('server_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=True)
    cluster = relationship(Cluster, backref=backref('servers', order_by=id))

    def __init__(self, id=None, name=None, cluster=None):
        self.id = id
        self.name = name
        self.cluster = cluster

    def __repr__(self):
        return make_repr(self)

################################################################################

class ChannelURLDef(Base):
    """ A channel's URL definition.
    """
    __tablename__ = 'channel_url_def'
    __table_args__ = (UniqueConstraint('cluster_id', 'url_pattern'), {})

    id = Column(Integer,  Sequence("channel_url_def_id_seq"), primary_key=True)
    url_pattern = Column(String(400), nullable=False)
    channel_type = Enum('soap', 'plain-http')

    cluster_id = Column(Integer, ForeignKey("cluster.id"), nullable=True)
    cluster = relationship(Cluster, backref=backref("channel_url_defs", order_by=id))

    def __init__(self, id=None, url_pattern=None, channel_type=None):
        self.id = id
        self.url_pattern = url_pattern
        self.channel_type = channel_type

    def __repr__(self):
        return make_repr(self)

################################################################################

class WSSDefinition(Base):
    """ A WS-Security definition.
    """
    __tablename__ = "wss_def"
    __table_args__ = (UniqueConstraint("cluster_id", "name"), {})

    id = Column(Integer,  Sequence("wss_def_id_seq"), primary_key=True)
    name = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    reject_empty_nonce_ts = Column(Boolean(), nullable=False)
    reject_stale_username = Column(Boolean(), nullable=False)
    expiry_limit = Column(Integer(), nullable=False)
    nonce_freshness = Column(Integer(), nullable=False)

    cluster_id = Column(Integer, ForeignKey("cluster.id"), nullable=False)
    cluster = relationship(Cluster, backref=backref("wss_defs", order_by=id))

    def __init__(self, id=None, name=None, username=None, password=None,
                 reject_empty_nonce_ts=None, reject_stale_username=None,
                 expiry_limit=None, nonce_freshness=None, cluster=None):
        self.id = id
        self.name = name
        self.username = username
        self.password = password
        self.reject_empty_nonce_ts = reject_empty_nonce_ts
        self.reject_stale_username = reject_stale_username
        self.expiry_limit = expiry_limit
        self.nonce_freshness = nonce_freshness
        self.cluster = cluster

    def __repr__(self):
        return make_repr(self)

class WSSDefinitionPassword(Base):
    """ A WS-Security definition's passwords.
    """
    __tablename__ = "wss_def_passwd"

    id = Column(Integer,  Sequence("wss_def_passwd_id_seq"), primary_key=True)
    password = Column(LargeBinary(200000), server_default="not-set-yet", nullable=False)
    server_key_hash = Column(LargeBinary(200000), server_default="not-set-yet", nullable=False)

    server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    server = relationship(Server, backref=backref("wss_def_passwords", order_by=id))

    wss_def_id = Column(Integer, ForeignKey("wss_def.id"), nullable=False)
    wss_def = relationship(WSSDefinition, backref=backref("wss_def_passwords", order_by=id))

    def __init__(self, id=None, password=None, server_key_hash=None, server_id=None,
                 server=None, wss_def_id=None, wss_def=None):
        self.id = id
        self.password = password
        self.server_key_hash = server_key_hash
        self.server_id = server_id
        self.server = server
        self.wss_def_id = wss_def_id
        self.wss_def = wss_def

    def __repr__(self):
        return make_repr(self)

################################################################################

class SQLConnectionPool(Base):
    """ An SQL connection pool.
    """
    __tablename__ = "sql_pool"
    __table_args__ = (UniqueConstraint("cluster_id", "name"), {})

    id = Column(Integer,  Sequence("sql_pool_id_seq"), primary_key=True)
    name = Column(String(200), nullable=False)
    user = Column(String(200), nullable=False)
    db_name = Column(String(200), nullable=False)
    engine = Column(String(200), nullable=False)
    extra = Column(LargeBinary(200000), nullable=True)
    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    pool_size = Column(Integer(), nullable=False)

    cluster_id = Column(Integer, ForeignKey("cluster.id"), nullable=False)
    cluster = relationship(Cluster, backref=backref("sql_pools", order_by=id))

    def __init__(self, id=None, name=None, db_name=None, user=None, engine=None,
                 extra=None, host=None, port=None, pool_size=None, cluster=None):
        self.id = id
        self.name = name
        self.db_name = db_name
        self.user = user
        self.engine = engine
        self.extra = extra
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.cluster = cluster

    def __repr__(self):
        return make_repr(self)

class SQLConnectionPoolPassword(Base):
    """ An SQL connection pool's passwords.
    """
    __tablename__ = "sql_pool_passwd"

    id = Column(Integer,  Sequence("sql_pool_id_seq"), primary_key=True)
    password = Column(LargeBinary(200000), server_default="not-set-yet", nullable=False)
    server_key_hash = Column(LargeBinary(200000), server_default="not-set-yet", nullable=False)

    server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    server = relationship(Server, backref=backref("sql_pool_passwords", order_by=id))

    sql_pool_id = Column(Integer, ForeignKey("sql_pool.id"), nullable=False)
    sql_pool = relationship(SQLConnectionPool, backref=backref("sql_pool_passwords", order_by=id))

    def __init__(self, id=None, password=None, server_key_hash=None, server_id=None,
                 server=None, sql_pool_id=None, sql_pool=None):
        self.id = id
        self.password = password
        self.server_key_hash = server_key_hash
        self.server_id = server_id
        self.server = server
        self.sql_pool_id = sql_pool_id
        self.sql_pool = sql_pool

    def __repr__(self):
        return make_repr(self)