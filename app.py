from flask import render_template, Flask
import serial
import threading
from flask_sqlalchemy import SQLAlchemy
import plotly.graph_objs as go
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
x_values = np.arange(1, 25)


COM_PORT = '/dev/ttyUSB0'

class MyData(db.Model):
    """ Defining USer DB Class """
    __tablename__ = "My Users"
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.String(20))
    humidity = db.Column(db.String(20))
    ppm = db.Column(db.String(20))

    def __init__(self, temperature, humidity, ppm):
        self.temperature = temperature
        self.humidity = humidity
        self.ppm = ppm

def serial_com():
    """ Serial Com Connector """
    return serial.Serial(
        port = COM_PORT,
        baudrate = 9600,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = 1
    )

def manage_data(serial_data):
    """ Manage Serial data and save to DB """
    try:
        data_save = serial_data.split(",")
        print(serial_data)
        new_data = MyData(
            temperature = str(data_save[0]),
            humidity = str(data_save[1]),
            ppm = str(data_save[2])
        )

        db.session.add(new_data)
        db.session.commit()
    except Exception as error:
        print(f"Saving Error: {error}")

# Pause the program for 1 second to avoid overworking the serial port
def serial_thread():
    """ Read Serial Data received from Arduino """
    ser = serial_com()
    while 1:
        try:
            # Start reading data using newline
            x=ser.readline()
            print(x)
        except Exception:
            # If error when capturing, then close and reconnect serial
            try:
                ser.close()
            except Exception:
                print("Serial ALready Closed")
            finally:
                ser = serial_com()


@app.route("/")
def home():
    """ render home page """
    y_values_1 = np.random.randint(26, 45, size=24)
    y_values_2 = np.random.randint(40, 60, size=24)
    y_values_3 = np.random.randint(1000, 2000, size=24)

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
    return render_template("index.html", graph_html_1=graph_html_1, graph_html_2=graph_html_2, graph_html_3=graph_html_3)

if __name__ == "__main__":
    # threading.Thread(target=serial_thread).start()
    app.run(host = "0.0.0.0", port=8080, debug=True)