import polars as pl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

import entity


# クロノスコープDBへの接続用URLの作成
load_dotenv()
chronous_user = os.getenv("CHRONOSCOPE_USER")
chronous_password = os.getenv("CHRONOSCOPE_PASSWORD")
chronous_host = os.getenv("CHRONOSCOPE_HOST")
chronous_port = os.getenv("CHRONOSCOPE_PORT")
chronous_dbname = os.getenv("CHRONOSCOPE_DB")
chronous_connection_url = (
    f"postgresql+psycopg2://{chronous_user}:{chronous_password}"
    f"@{chronous_host}:{chronous_port}/{chronous_dbname}"
)

# engineオブジェクト作成
chronous_engine = create_engine(chronous_connection_url)

# DBセッションオブジェクトの作成
chronous_session_maker = sessionmaker(bind=chronous_engine)

# ormオブジェクトを作成
orm_trip = entity.TripMean
orm_route = entity.RouteMean


def get_all_trip_mean(route_id):
    with chronous_session_maker() as session:
        target_records = (
            session
            .query(orm_trip)
            .filter(orm_trip.route_id == route_id)
            .all()
        )

        df = to_df(
            orm_model=orm_trip,
            records=target_records
        )

    return df


def get_route_mean(route_id):
    with chronous_session_maker() as session:
        target_records = (
            session
            .query(orm_route)
            .filter(orm_route.route_id == route_id)
            .all()
        )

        df = to_df(
            orm_model=orm_route,
            records=target_records
        )

    return df


def to_df(
        orm_model,
        records: list
):
    column_names = [
        column.name
        for column
        in orm_model.__table__.columns
    ]

    data = {}
    # 取得レコードが一つの場合
    if len(records) == 1:
        for column_name in column_names:
            data[column_name] = getattr(records[0], column_name)
    else:
        # 取得レコードが複数の場合
        for column_name in column_names:
            temp = []
            for record in records:
                temp.append(getattr(record, column_name))
            data[column_name] = temp

    df = pl.DataFrame(data, schema=column_names)

    return df
