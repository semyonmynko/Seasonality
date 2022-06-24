import sqlite3
from flask import Flask, render_template
from flasgger import Swagger
import pandas as pd
import json
import plotly
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose

app = Flask(__name__)
swagger = Swagger(app)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def line():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM db').fetchall()
    conn.close()

    df = pd.DataFrame(data, columns=['id','code','date','num_1','num_2','num_3','num_4'])
    df['date'] = df['date'].astype('datetime64')
    df = df.drop(columns=['code', 'id'])
    df_series = df.set_index('date').asfreq('D')
    df_series  = df_series.interpolate(method='time')
    seasonal = pd.DataFrame()
    for i in range(1, 5):
        analysis = df_series[[f'num_{i}']].copy()
        decompose_result_mult = seasonal_decompose(analysis, model="multiplicative", period=365)
        seasonal[f'num_{i}'] = decompose_result_mult.seasonal
    seasonal = seasonal.reset_index()

    fig = px.line(df, x="date", y=df.columns,
              hover_data={"date": "|%B %d, %Y"},
              title='Price history')
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(count=10, label="10y", step="year", stepmode="backward"),
            dict(step="all")
            ])
        )
    )
    fig_1 = px.line(seasonal, x="date", y=seasonal.columns,
              hover_data={"date": "|%B %d, %Y"},
              title='Seasonality')
    fig_1.update_xaxes(rangeslider_visible=True)
    fig_1.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(count=10, label="10y", step="year", stepmode="backward"),
            dict(step="all")
            ])
        )
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON1 = json.dumps(fig_1, cls=plotly.utils.PlotlyJSONEncoder)
    header="Timeseries"
    description = """"""
    return render_template('line_chart.html', graphJSON=graphJSON,graphJSON1=graphJSON1, header=header,description=description)