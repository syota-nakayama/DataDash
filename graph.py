import plotly.graph_objs as go
import plotly.express as px
import polars as pl


def create_line(target_data, route_mean, type):
    fig = go.Figure()
    route_name = ""

    for row in target_data.iter_rows(named=True):
        if type == "date":
            fig.add_trace(
                go.Scatter(
                    y=row["delay"],
                    mode="lines",
                    name=str(row["date"]),
                    line=dict(width=2, color="#636efa")
                )
            )

        if type == "trip_id":
            fig.add_trace(
                go.Scatter(
                    y=row["delay"],
                    mode="lines",
                    name=str(row["trip_id"]),
                    line=dict(width=2, color="#636efa")
                )
            )

        route_name = row["route_id"]

    fig.add_trace(
        go.Scatter(
            y=route_mean["delay"].to_list(),
            mode="lines",
            name="路線の全データの平均",
            line=dict(width=4, color="lightgreen")
        )
    )

    fig.update_layout(
        #title=f"{route_name}の遅延推移",
        xaxis_title="停留所番号",
        yaxis_title="遅延時間（秒）",
        template="plotly_dark",
        showlegend=False,  # 凡例多すぎるなら消す
        height=700,
        plot_bgcolor='rgba(0,0,0,0)',  # グラフ内部
        paper_bgcolor='rgba(0,0,0,0)',  # グラフ全体
        font_color='white',
        xaxis_title_font=dict(size=27),
        yaxis_title_font=dict(size=27),
    )
    fig.add_hline(
        y=0,
        line=dict(color="white", width=1, dash="dot")
    )

    return fig


def create_box(target_data):
    df_list = []

    for row in target_data.iter_rows(named=True):
        df_row = pl.DataFrame(
            [row["delay"]],
            schema=[
                f"{i}" for i in range(len(row["delay"]))
            ],
            orient="row"
        )
        df_list.append(df_row)

    box_data = pl.concat(df_list)
    fig = px.box(
        box_data
    )
    fig.update_layout(
        xaxis_title="停留所番号",
        yaxis_title="遅延時間（秒）",
        template="plotly_dark",
        showlegend=False,
        height=600,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_title_font=dict(size=27),
        yaxis_title_font=dict(size=27),
    )

    fig.add_hline(
        y=0,
        line=dict(color="white", width=1, dash="dot")
    )

    return fig


def create_hist(target_data):
    rows = []

    for row in target_data.iter_rows(named=True):
        # ヒストグラムの作成
        x_line = [
            i for i in range(len(row["delay"]))
        ]
        for sequence, delay in zip(x_line, row["delay"]):
            rows.append({"stop_sequence": sequence, "delay": delay})

    # 2D ヒストグラム等高線
    hist_df = pl.DataFrame(rows)
    fig = px.density_contour(
        hist_df,
        x="stop_sequence",
        y="delay"
    )
    fig.update_traces(
        contours_coloring="fill",
        contours_showlabels=True
    )
    fig.update_layout(
        xaxis_title="停留所番号",
        yaxis_title="遅延時間（秒）",
        template="plotly_dark",
        showlegend=False,
        height=600,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_title_font=dict(size=27),
        yaxis_title_font=dict(size=27),
    )
    fig.add_hline(
        y=0,
        line=dict(color="white", width=1, dash="dot")
    )

    return fig


def update_map(df, selected_seq, zoom_value):
    fig = px.scatter_mapbox(
        df,
        lat="stop_lat",
        lon="stop_lon",
        hover_name="stop_name",
        zoom=zoom_value,
        height=900
    )
    # 背景タイル
    fig.update_layout(
        mapbox_style="open-street-map",
        template="plotly_dark",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',  # グラフ内部
        paper_bgcolor='rgba(0,0,0,0)',  # グラフ全体
        font_color='white',
        xaxis_title_font=dict(size=27),
        yaxis_title_font=dict(size=27),
    )

    # 現在選択された停留所を強調
    fig.update_traces(
        marker=dict(size=10, color="#0066FF")
    )
    highlighted = df.filter(pl.col("stop_sequence") == selected_seq)
    fig.add_scattermapbox(
        lat=highlighted["stop_lat"],
        lon=highlighted["stop_lon"],
        mode="markers",
        textposition="top right",
        marker=dict(size=20, color="#FF3D00"),
        hovertext=highlighted["stop_name"]
    )

    return fig
