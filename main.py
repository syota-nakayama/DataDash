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

# 折れ線グラフ作成
route_name = ""
df_list = []
for row in all_trip_mean.iter_rows(named=True):
    # 折れ線グラフ
    fig_line.add_trace(
        go.Scatter(
            y=row["delay_mean"],
            mode="lines",
            name=row["trip_id"],
            line=dict(width=1, color="#636efa")
        )
    )

    # 箱ひげ図用データの作成
    df_row = pl.DataFrame(
        [row["delay_mean"]],
        schema=[
            f"{i}" for i in range(len(row["delay_mean"]))
        ],
        orient="row"
    )
    df_list.append(df_row)

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
print(box_data)
fig_box = px.box(
    box_data
)

fig_box.update_layout(
    xaxis_title="停留所番号",
    yaxis_title="遅延時間（秒）",
    template="plotly_dark",
    showlegend=False
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
    ]
)

# 実行
if __name__ == "__main__":
    app.run(debug=True)
