import time
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
y_values_1 = []
y_values_2 = []
y_values_3 = []


COM_PORT = '/dev/ttyUSB0'

class MyData(db.Model):
    """ Defining USer DB Class """
    __tablename__ = "My Query Datas"
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

def serial_thread():
    """ Read Serial Data received from Arduino """
    ser = serial_com()
    while 1:
        time.sleep(.1)
        try:
            # Start reading data using newline
            x=ser.readline()
            print(x)
            manage_data(x)
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
    global y_values_1
    global y_values_2
    global y_values_3
    current_temp = ""
    current_humd = ""
    current_ammo = ""

    with app.app_context():
        datas = MyData.query.all()
        for data in datas:
            y_values_1.append(int(data.temperature))
            current_temp = data.temperature
            y_values_2.append(int(data.humidity))
            current_humd = data.humidity
            y_values_3.append(int(data.ppm))
            current_ammo = data.ppm

    graph_1 = go.Scatter(x=x_values, y=y_values_1, mode='lines+markers')
    graph_2 = go.Scatter(x=x_values, y=y_values_2, mode='lines+markers')
    graph_3 = go.Scatter(x=x_values, y=y_values_3, mode='lines+markers')

    layout_1 = go.Layout(
        title='Temperature',
        xaxis=dict(title='Hour'),
        yaxis=dict(title='Temperature')
    )
    layout_2 = go.Layout(title='Humidity', xaxis=dict(title='Hour'), yaxis=dict(title='Humidity'))
    layout_3 = go.Layout(
        title='Ammonia Particles',
        xaxis=dict(title='Hour'),
        yaxis=dict(title='PPM')
    )

    figure_1 = go.Figure(data=[graph_1], layout=layout_1)
    figure_2 = go.Figure(data=[graph_2], layout=layout_2)
    figure_3 = go.Figure(data=[graph_3], layout=layout_3)

    graph_html_1 = figure_1.to_html(full_html=False)
    graph_html_2 = figure_2.to_html(full_html=False)
    graph_html_3 = figure_3.to_html(full_html=False)

    template_data = {
        "current_temp": current_temp,
        "current_humd": current_humd,
        "current_ammo": current_ammo,
        "graph_html_1": graph_html_1, 
        "graph_html_2": graph_html_2,
        "graph_html_3": graph_html_3
    }
    return render_template("index.html", **template_data)

@app.route("/stream")
def stream():
    return render_template("cam_view.html")

if __name__ == "__main__":
    # threading.Thread(target=serial_thread).start()

    with app.app_context():
        db.create_all()
    app.run(host = "0.0.0.0", port=8080, debug=True)
