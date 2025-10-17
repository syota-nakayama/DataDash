from dash import Dash, dcc, html, Input, Output
import argparse
import polars as pl
import datastore
import graph


# コマンドライン引数
parser = argparse.ArgumentParser(description="Example script")

# 引数の設定
parser.add_argument(
    "--type",
    type=str,
    help="表示させるデータ群を入力してください"
)
parser.add_argument(
    "--route",
    type=str,
    help="route_idを入力してください"
)
parser.add_argument(
    "--trip",
    type=str,
    help="trip_idを入力してください"
)
args = parser.parse_args()

# Dashアプリ作成
app = Dash(__name__)

# データ取得
all_trip_mean = datastore.get_all_trip_mean(args.route)
route_mean = datastore.get_route_mean(args.route)
trip_data = datastore.get_operation_data(args.trip)
map_data = datastore.get_stops_info(args.trip)

# グラフオブジェクトの作成
if args.type == "date":
    fig_line = graph.create_line(trip_data, route_mean, "date")
    fig_box = graph.create_box(trip_data)
    fig_histgram = graph.create_hist(trip_data)
elif args.type == "trip":
    fig_line = graph.create_line(all_trip_mean, route_mean, "trip_id")
    fig_box = graph.create_box(all_trip_mean)
    fig_histgram = graph.create_hist(all_trip_mean)

# Dashレイアウト
app.layout = html.Div(
    children=[
        html.H1("バス運行データ可視化ダッシュボード"),

        # 折れ線グラフ
        dcc.Graph(
            figure=fig_line,
            style={"backgroundColor": "black"}
        ),

        # 箱ひげ図
        dcc.Graph(
            figure=fig_box,
            style={"backgroundColor": "black"}
        ),

        # 2D ヒストグラム等高線
        dcc.Graph(
            figure=fig_histgram,
            style={"backgroundColor": "black"}
        ),

        # バス停マップ
        dcc.Graph(
            id="bus-map",
            style={"backgroundColor": "black"}
        ),

        # スライダー
        dcc.Slider(
            id="seq-slider",
            min=map_data["stop_sequence"].min(),
            max=map_data["stop_sequence"].max(),
            step=1,
            value=map_data["stop_sequence"].min(),
            marks={
                i: str(i)
                for i in map_data["stop_sequence"]
            },
            included=True,
            updatemode='drag',
            tooltip={
             "always_visible": True,
             "style": {"color": "black", "fontSize": "20px"},
            }
        )
    ]
)


@app.callback(
        Output("bus-map", "figure"),
        Input("seq-slider", "value")
)
def create_map(selected_seq):
    return graph.update_map(map_data, selected_seq)


# 実行
if __name__ == "__main__":
    app.run(debug=True)
