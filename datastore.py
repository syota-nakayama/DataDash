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

# ヒストリアDB接続用URLの作成
historia_user = os.getenv("HISTORIA_USER")
historia_password = os.getenv("HISTORIA_PASSWORD")
historia_host = os.getenv("HISTORIA_HOST")
historia_port = os.getenv("HISTORIA_PORT")
historia_dbname = "kitami"
historia_connection_url = (
    f"postgresql+psycopg2://{historia_user}:{historia_password}"
    f"@{historia_host}:{historia_port}/{historia_dbname}"
)

# engineオブジェクト作成
chronous_engine = create_engine(chronous_connection_url)
historia_engine = create_engine(historia_connection_url)

# DBセッションオブジェクトの作成
chronous_session_maker = sessionmaker(bind=chronous_engine)
historia_session_maker = sessionmaker(bind=historia_engine)

# ormオブジェクトを作成
orm_trip = entity.TripMean
orm_route = entity.RouteMean
orm_operation = entity.Operation


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


def get_operation_data(trip_id_list):
    target_df = pl.DataFrame()
    with chronous_session_maker() as session:
        for trip_id in trip_id_list:
            target_records = (
                session
                .query(orm_operation)
                .filter(orm_operation.trip_id == trip_id)
                .all()
            )

            df = to_df(
                orm_model=orm_operation,
                records=target_records
            )

            target_df = pl.concat([target_df, df])

    return target_df



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


def get_stops_info(trip_id):
    # stop_times(取得カラム：trip_id,stop_id,stop_sequence)からtrip_idを指定してデータを取得
    with historia_session_maker() as session:
        stops = (
            session
            .query(entity.Stop)
            .all()
        )
        stop_times = (
            session
            .query(entity.StopTime)
            .filter(entity.StopTime.trip_id == trip_id)
            .all()
        )
        # dfに変換
        stops_df = to_df(
            orm_model=entity.Stop,
            records=stops
        )
        stop_times_df = to_df(
            orm_model=entity.StopTime,
            records=stop_times
        )

    # stop_timesデータを軸に共有結合(必要カラム:stop_name,lat,lon,sequence)
    df = stop_times_df.join(stops_df, on="stop_id", how="inner")

    df = (
        df
        .select(
            "stop_name",
            "stop_lat",
            "stop_lon",
            "stop_sequence"
        )
        .sort("stop_sequence")
    )

    df = df.with_columns(
        [
            pl.Series(
                name="stop_name",
                values=[to_fullwidth(x) for x in df["stop_name"]]
            )
        ]
    )

    return df


# 半角数字・英字 → 全角に変換
def to_fullwidth(s):
    if s is None:
        return s
    return "".join(chr(ord(c)+0xFEE0) if 0x21 <= ord(c) <= 0x7E else c for c in s)


def get_route_trip_dict():
    target_dict = {}
    with chronous_session_maker() as session:
        target_records = (
            session
            .query(orm_route)
            .all()
        )

        route_df = to_df(
            orm_model=orm_route,
            records=target_records
        )

    route_list = route_df["route_id"].to_list()

    for route_id in route_list:
        with chronous_session_maker() as session:
            target_records = (
                session
                .query(orm_trip)
                .filter(orm_trip.route_id == route_id)
                .all()
            )

            trip_df = to_df(
                orm_model=orm_trip,
                records=target_records
            )

            trip_list = trip_df["trip_id"].to_list()
            trip_list.append("便平均")

            target_dict[route_id] = trip_list

    return target_dict
