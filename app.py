import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 创建Dash应用
app = dash.Dash(__name__)

file_path = 'owid-covid-data.csv'

# 读取数据集
covid_data = pd.read_csv(file_path)

# 筛选时间范围：2021年1月1日至2021年12月31日
covid_data['date'] = pd.to_datetime(covid_data['date'])  # 确保日期列是日期格式
start_date = '2021-01-01'
end_date = '2021-12-31'
mask = (covid_data['date'] >= start_date) & (covid_data['date'] <= end_date)
filtered_data = covid_data.loc[mask]

# 选择需要的列：国家/地区代码，日期，新增数，确诊数，死亡数
selected_columns = ['iso_code', 'location', 'date', 'new_cases', 'total_cases', 'new_deaths']
processed_data = filtered_data[selected_columns].copy()  # 添加 .copy() 来创建副本

# 转换日期格式并排序
processed_data['date'] = pd.to_datetime(processed_data['date']).dt.strftime('%Y-%m-%d')
processed_data.sort_values('date', inplace=True)

countries = processed_data['location'].unique()
country_options = [{'label': country, 'value': country} for country in countries]

# Dash应用布局
app.layout = html.Div([
    # 单选按钮，用于选择数据类型
    dcc.RadioItems(
        id='data-type-selector',
        options=[
            {'label': 'Total cases', 'value': 'total_cases'},
            {'label': 'Deaths', 'value': 'new_deaths'},
            {'label': 'New cases', 'value': 'new_cases'}
        ],
        value='total_cases'  # 默认值
    ),
    dcc.Dropdown(
        id='country-selector',
        options=country_options,
        value=['Ireland'],  # 将默认值设置为列表
        multi=True  # 允许选择多个国家
    ),
    # 用于显示地图的图表组件
    dcc.Graph(id='covid-map'),
    dcc.Graph(id='country-trend')
])

@app.callback(
    Output('covid-map', 'figure'),
    [Input('data-type-selector', 'value'),
     Input('country-selector', 'value')]
)
def update_map(selected_data_type, selected_countries):
    # 如果没有国家被选中，则显示所有国家
    if selected_countries:
        filtered_data = processed_data[processed_data['location'].isin(selected_countries)]
    else:
        filtered_data = processed_data

    # 创建地图
    fig = px.choropleth(
        filtered_data,
        locations="iso_code",
        color=selected_data_type,
        hover_name="location",
        animation_frame="date",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Data: {selected_data_type}",
    )
    return fig
@app.callback(
    Output('country-trend', 'figure'),
    [Input('data-type-selector', 'value'),
     Input('country-selector', 'value')]
)
def update_country_trend(selected_data_type, selected_countries):
    # 确保选择了一个且仅一个国家
    if selected_countries and len(selected_countries) == 1:
        country_data = processed_data[processed_data['location'] == selected_countries[0]]
        fig = px.line(
            country_data,
            x='date',
            y=selected_data_type,
            title=f"{selected_countries[0]}: {selected_data_type} over time"
        )
    else:
        fig = px.line(title="Please select a single country to view trends.")

    return fig

# 运行Dash应用
if __name__ == '__main__':
    app.run_server(debug=True)
