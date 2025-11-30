from dash import Dash, dcc, html, Input, Output, callback_context, State
import datastore
import graph

# Dashアプリ作成
app = Dash(__name__)

# プルダウン選択肢
routes = datastore.get_route_trip_dict()

# mapの初期値
#map_data = datastore.get_stops_info("平日_12時02分_系統106")
#slider_max = 30

# Dashレイアウト
app.layout = html.Div(
    style={
            # グラデーション（左上→右下に紫→黒）
            "minHeight": "100vh",
            "padding": "30px",
            "color": "white",
            "fontFamily": "sans-serif",
            "background": "linear-gradient(to bottom, #000000 0%, #1a0a4a 4%, #2e0b5a 50%, #3a0ca3 75%, #7209b7 100%)",
            "backgroundSize": "400% 400%",
            "animation": "gradientMove 15s ease infinite"
        },
    children=[
        html.H1("バス運行データ可視化ダッシュボード"),

        # 路線選択ドロップダウン
        html.H2("1. 路線を選択してください"),
        dcc.Dropdown(
            id="route-dropdown",
            options=[{"label": k, "value": k} for k in routes],
            value="",  # 初期値
            style={
                "width": "500px",
                "fontSize": "23px",
                "padding": "6px",
                "backgroundColor": "#1f0c40",  # 背景色（濃い紫）
                "color": "white",               # 文字色
                "border": "1px solid #7209b7",  # 枠線
                "borderRadius": "8px",
                "boxShadow": "0 0 10px rgba(114, 9, 183, 0.5)"  # ちょっと浮かせる
            },
        ),

        html.H2("2. 便を選択してください"),

        # 便選択ドロップダウン
        dcc.Dropdown(
            id="trip-dropdown",
            style={
                "width": "500px",
                "fontSize": "23px",
                "padding": "6px",
                "backgroundColor": "#1f0c40",  # 背景色（濃い紫）
                "color": "white",               # 文字色
                "border": "1px solid #7209b7",  # 枠線
                "borderRadius": "8px",
                "boxShadow": "0 0 10px rgba(114, 9, 183, 0.5)"  # ちょっと浮かせる
            },
            multi=True
        ),

        # 更新ボタン
        html.H2("3. ボタンを押してグラフを描画してください"),
        html.Button(
            "▷︎ 描画",
            id="update-btn",
            n_clicks=0,
            style={
                "backgroundColor": "#8a2be2",
                   "color": "white",
                   "border": "none",
                   "padding": "10px 20px",
                   "borderRadius": "8px",
                   "cursor": "pointer",
                   "fontSize": "23px",
                   "transition": "0.3s",
                   "marginBottom": "20px",
                   "boxShadow": "0 0 10px rgba(114, 9, 183, 0.5)"
            },
            title="クリックして描画"
        ),

        # 折れ線グラフ
        dcc.Graph(
            id="graph_line",
            style={"backgroundColor": "black"}
        ),

        # 箱ひげ図
        dcc.Graph(
            id="graph_box",
            style={"backgroundColor": "black"}
        ),

        # 2D ヒストグラム等高線
        dcc.Graph(
            id="graph_hist",
            style={"backgroundColor": "black"}
        ),
    ]
)

"""

        # マップのズーム設定
        html.H2("地図のズーム設定ができます"),
        html.Br(),
        html.Br(),
        dcc.Slider(
            id="zoom-slider",
            min=0,
            max=20,
            step=1,
            value=13,
            updatemode='drag',
            tooltip={
                "always_visible": True,
                "style": {"color": "black", "fontSize": "25px"},
            }
        ),

        # スライダー
        html.H2("バス停の場所がわかります"),
        html.Br(),
        html.Br(),
        dcc.Slider(
            id="seq-slider",
            min=1,
            max=slider_max,  # 初期値
            step=1,
            value=10,  # 初期値
            included=True,
            updatemode='drag',
            tooltip={
                "always_visible": True,
                "style": {"color": "black", "fontSize": "25px"},
            }
        ),

        # バス停マップ
        dcc.Graph(
            id="bus-map",
            #style={"backgroundColor": "black"}
        ),
        """

# 路線が決まれば、便が決まるドロップダウン
@app.callback(
    Output("trip-dropdown", "options"),
    Input("route-dropdown", "value"),
    prevent_initial_call=True  # 初期起動時には呼ばれない
)
def update_trip_options(selected_route):
    trips = routes[selected_route]
    return [{"label": t, "value": t} for t in trips]

"""
# バス停のスライドバー
@app.callback(
    Output("bus-map", "figure"),
    Output("seq-slider", "max", allow_duplicate=True),
    Input("seq-slider", "value"),
    Input("zoom-slider", "value"),
    prevent_initial_call=True  # 初期起動時には呼ばれない
)
def create_map(selected_seq, zoom_value):
    return graph.update_map(map_data, selected_seq, zoom_value), map_data["stop_sequence"].max()
"""

# updateボタン
@app.callback(
    [
        Output("graph_line", "figure"),
        Output("graph_box", "figure"),
        Output("graph_hist", "figure"),
        #Output("bus-map", "figure", allow_duplicate=True),
        #Output("seq-slider", "max")

    ],
    Input("update-btn", "n_clicks"),
    [
        State("route-dropdown", "value"),
        State("trip-dropdown", "value")
    ],
    prevent_initial_call=True  # 初期起動時には呼ばれない
)
def update_graph(clicks, route, trip):
    # コールバック内で最新の値を取得
    route = callback_context.states["route-dropdown.value"]
    trip_list = callback_context.states["trip-dropdown.value"]

    # データ取得
    all_trip_mean = datastore.get_all_trip_mean(route)
    route_mean = datastore.get_route_mean(route)

    # 再描画
    if trip_list == ["便平均"]:
        # 描画
        fig_line = graph.create_line(all_trip_mean, route_mean, "trip_id")
        fig_box = graph.create_box(all_trip_mean)
        fig_histgram = graph.create_hist(all_trip_mean)
    else:
        # データ取得
        trip_data = datastore.get_operation_data(trip_list)
        # 描画
        fig_line = graph.create_line(trip_data, route_mean, "date")
        fig_box = graph.create_box(trip_data)
        fig_histgram = graph.create_hist(trip_data)

    """
    global map_data
    trip_list = routes[route]
    map_data = datastore.get_stops_info(trip_list[0])
    graph_map = graph.update_map(map_data, 1, 13)
    max_sequence = map_data["stop_sequence"].max()
    """

    return fig_line, fig_box, fig_histgram #,graph_map, max_sequence


# 実行
if __name__ == "__main__":
    app.run(debug=True)
