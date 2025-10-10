from dash import Dash, dcc, html
import plotly.graph_objs as go
import plotly.express as px
import polars as pl

import datastore

# Dashアプリ作成
app = Dash(__name__)

# Figure作成
fig_line = go.Figure()

# データ取得
all_trip_mean = datastore.get_all_trip_mean("②美山線(114)")
route_mean = datastore.get_route_mean("②美山線(114)")
trip_data = datastore.get_operation_data("土日祝_06時55分_系統114")

# 折れ線グラフ作成
route_name = ""
df_list = []
# 一時的にためるリスト
rows = []
for row in trip_data.iter_rows(named=True):
    # 折れ線グラフ
    fig_line.add_trace(
        go.Scatter(
            y=row["delay"],
            mode="lines",
            name=str(row["date"]),
            line=dict(width=2, color="#636efa")
        )
    )

    # 箱ひげ図用データの作成
    df_row = pl.DataFrame(
        [row["delay"]],
        schema=[
            f"{i}" for i in range(len(row["delay"]))
        ],
        orient="row"
    )
    df_list.append(df_row)

    # ヒストグラムの作成
    x_line = [
        i for i in range(len(row["delay"]))
    ]
    for sequence, delay in zip(x_line, row["delay"]):
        rows.append({"stop_sequence": sequence, "delay": delay})

    route_name = row["route_id"]

fig_line.add_trace(
    go.Scatter(
        y=route_mean["delay_mean"].to_list(),
        mode="lines",
        name="routeの平均",
        line=dict(width=4, color="white")
    )
)

fig_line.update_layout(
    title=f"{route_name}の遅延推移",
    xaxis_title="停留所番号",
    yaxis_title="遅延時間（秒）",
    template="plotly_dark",
    showlegend=False  # 凡例多すぎるなら消す
)

# 箱ひげ図
box_data = pl.concat(df_list)
fig_box = px.box(
    box_data
)
fig_box.update_layout(
    xaxis_title="停留所番号",
    yaxis_title="遅延時間（秒）",
    template="plotly_dark",
    showlegend=False
)

# 2D ヒストグラム等高線
hist_df = pl.DataFrame(rows)
fig_histgram = px.density_contour(
    hist_df,
    x="stop_sequence",
    y="delay"
)
fig_histgram.update_traces(
    contours_coloring="fill",
    contours_showlabels=True
)
fig_histgram.update_layout(
    xaxis_title="停留所番号",
    yaxis_title="遅延時間（秒）",
    template="plotly_dark",
    showlegend=False,
    height=700
)

# Dashレイアウト
app.layout = html.Div(
    children=[
        html.H2("バス運行データ可視化ダッシュボード"),

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
        )
    ]
)

# 実行
if __name__ == "__main__":
    app.run(debug=True)
