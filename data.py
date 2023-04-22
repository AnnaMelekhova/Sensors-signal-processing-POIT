import serial
import json

ser = serial.Serial("/dev/ttyS0")
ser.baudrate = 9600
ser.flushInput()

while 1 :
    line = ser.readline().decode('utf-8').rstrip()
    
    data = json.loads(line)
    
    temp = data['temperature']
    hum = data['humidity']
    dist = data['distance']
    ir = data['ir']
    
    print('Temperature: ', temp, 'C')
    print('Humidity: ', hum, '%')
    print('Distance: ', dist, 'cm')
    print('Ir Value: ', 'Zavadzas' if ir == 0 else 'Nevidim ta')
    print('\n--------------------\n')
    