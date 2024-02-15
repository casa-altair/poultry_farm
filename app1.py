from flask import Flask, render_template
import plotly.graph_objs as go
import numpy as np

app = Flask(__name__)

# Generate x-axis values for 24 hours
x_values = np.arange(1, 25)

# Sample data for the graphs
y_values_1 = np.random.randint(26, 45, size=24)
y_values_2 = np.random.randint(40, 60, size=24)
y_values_3 = np.random.randint(1000, 2000, size=24)

@app.route('/')
def index():
    # Create three Plotly graphs
    graph_1 = go.Scatter(x=x_values, y=y_values_1, mode='lines+markers')
    graph_2 = go.Scatter(x=x_values, y=y_values_2, mode='lines+markers')
    graph_3 = go.Scatter(x=x_values, y=y_values_3, mode='lines+markers')

    layout_1 = go.Layout(title='Temperature', xaxis=dict(title='Hour'), yaxis=dict(title='Temperature'))
    layout_2 = go.Layout(title='Humidity', xaxis=dict(title='Hour'), yaxis=dict(title='Humidity'))
    layout_3 = go.Layout(title='Ammonia Particles', xaxis=dict(title='Hour'), yaxis=dict(title='PPM'))

    figure_1 = go.Figure(data=[graph_1], layout=layout_1)
    figure_2 = go.Figure(data=[graph_2], layout=layout_2)
    figure_3 = go.Figure(data=[graph_3], layout=layout_3)

    graph_html_1 = figure_1.to_html(full_html=False)
    graph_html_2 = figure_2.to_html(full_html=False)
    graph_html_3 = figure_3.to_html(full_html=False)

    return render_template('graph.html', graph_html_1=graph_html_1, graph_html_2=graph_html_2, graph_html_3=graph_html_3)

if __name__ == '__main__':
    app.run(debug=True)
