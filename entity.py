from sqlalchemy import Column, TEXT, PrimaryKeyConstraint, Integer, ARRAY, Date, NUMERIC
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TripMean(Base):
    __tablename__ = "trip_mean"
    __table_args__ = (
        PrimaryKeyConstraint(
            "route_id",
            "trip_id"
        ),
        {"schema": "kitami", "extend_existing": True}
    )

    route_id = Column(TEXT)
    trip_id = Column(TEXT)
    delay = Column(ARRAY(Integer))


class RouteMean(Base):
    __tablename__ = "route_mean"
    __table_args__ = {"schema": "kitami", "extend_existing": True}

    route_id = Column(TEXT, primary_key=True)
    delay = Column(ARRAY(Integer))


class Operation(Base):
    __tablename__ = "operation"
    __table_args__ = (
        PrimaryKeyConstraint(
            "route_id",
            "trip_id",
            "date"
        ),
        {"schema": "kitami",  "extend_existing": True}
    )

    route_id = Column(TEXT)
    trip_id = Column(TEXT)
    date = Column(Date)
    delay = Column(ARRAY(Integer))


class StopTime(Base):
    __tablename__ = "stop_times"
    __table_args__ = (
        PrimaryKeyConstraint(
            "trip_id",
            "stop_sequence"
        ),
        {"schema": "duration_0001",  "extend_existing": True}
    )

    trip_id = Column(TEXT)
    stop_id = Column(TEXT)
    stop_sequence = Column(Integer)


class Stop(Base):
    __tablename__ = "stops"
    __table_args__ = {"schema": "duration_0001",  "extend_existing": True}

    stop_id = Column(TEXT, primary_key=True)
    stop_name = Column(TEXT)
    stop_lat = Column(NUMERIC)
    stop_lon = Column(NUMERIC)
