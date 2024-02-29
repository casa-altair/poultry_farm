""" Main app """
import time
from flask import render_template, Flask
import serial
import threading
from flask_sqlalchemy import SQLAlchemy
import numpy as np



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
x_values = [1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
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
    y_values_1 = []
    y_values_2 = []
    y_values_3 = []
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
    temp = {
        'labels': x_values,
        'values': y_values_1,
        'x_title': 'Hours',
        'y_title': 'Temperature (in C)'
    }
    humd = {
        'labels': x_values,
        'values': y_values_2,
        'x_title': 'Hours',
        'y_title': 'Humidity'
    }
    ppm = {
        'labels': x_values,
        'values': y_values_3,
        'x_title': 'Hours',
        'y_title': 'PPM'
    }
    print(current_temp)
    print(current_humd)
    print(current_ammo)
    print(temp)
    print()
    print(humd)
    print()
    print(ppm)
    print()

    return render_template(
        "index.html",
        current_temp=current_temp,
        current_humd=current_humd,
        current_ammo=current_ammo,
        graph_html_1=temp,
        graph_html_2=humd,
        graph_html_3=ppm
    )

@app.route("/stream")
def stream():
    return render_template("cam_view.html")

if __name__ == "__main__":
    # threading.Thread(target=serial_thread).start()

    with app.app_context():
        db.create_all()
    app.run(port=8080, debug=True)
