from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect    
import time
import random
import json
import serial
async_mode = None
import MySQLdb 
import configparser as ConfigParser
async_mode = None

app = Flask(__name__)

# config = ConfigParser.ConfigParser()
# config.read('config.cfg')
# myhost = config.get('mysqlDB', 'host')
# myuser = config.get('mysqlDB', 'user')
# mypasswd = config.get('mysqlDB', 'passwd')
# mydb = config.get('mysqlDB', 'db')
# print(myhost)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser = serial.Serial("/dev/ttyS0")
ser.baudrate = 9600
ser.flushInput()

def background_thread(args):
    count = 0    
    dataCounter = 0
    # db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    dataList = []
    i = 0
    while True:
        if args:
          A = dict(args).get('A')
          btnV = dict(args).get('btn_value')
        else:
          A = 1
          btnV = 'null' 
        
        socketio.sleep(2)
        count +=1
        ###############SENSOR DATA#####################
        #line = ser.readline().decode('utf-8').rstrip()
        #data = json.loads(line)
        ###############SENSOR DATA#####################
        
        ###############TEST DATA######################
        f = open('dummydata.json')
        line = json.load(f)
        data = line[i]
        ###############TEST DATA######################
        temp = data['temperature']
        hum = data['humidity']
        dist = data['distance']
        ir = data['ir']
        
        dataDict = {
             "time": count,
             "t": temp,
             "h": hum,
             "d": dist,
             "ir": ir}
        dataList.append(dataDict)
        
        i = i+1
        if len(dataList)>0:
            print(str(dataList))
            print(str(dataList).replace("'", "\""))
        socketio.emit('my_response',
                      {'data': dataDict, 'count': count},
                      namespace='/test')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
    
@app.route('/graphlive', methods=['GET', 'POST'])
def graphlive():
    return render_template('graphlive.html', async_mode=socketio.async_mode)
  
@app.route('/gauge', methods=['GET', 'POST'])
def gauge():
    return render_template('gauge.html', async_mode=socketio.async_mode)

@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']    

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
