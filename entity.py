from sqlalchemy import Column, TEXT, PrimaryKeyConstraint, Integer, ARRAY
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
    delay_mean = Column(ARRAY(Integer))


class RouteMean(Base):
    __tablename__ = "route_mean"
    __table_args__ = {"schema": "kitami", "extend_existing": True}

    route_id = Column(TEXT, primary_key=True)
    delay_mean = Column(ARRAY(Integer))
