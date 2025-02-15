import socket
import time
import json
import os
import threading
import logging

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

sock = socket.socket()

with open("config.json", "r") as f:
    global config
    config = json.load(f)

try:
    sock.bind(('', config["host"]))
    print(f"Using port {config['host']}")
except OSError:
    sock.bind(('', 8080))
    print("Using port 8080")

sock.listen(5)

def work(msg, conn, addr):
    print("Connected", addr)

    rash = msg.split('.')[1]
    if rash not in ('html','css','js', 'min', 'jpeg', 'png'):
        logging.info(f' {msg} - {addr[0]} - 403 forbidden')
        status = "HTTP/1.1 403 forbidden\n"
        msg = '403.html'
    else:
        logging.info(f'{msg} - {addr[0]} - 200 OK')
        status = "HTTP/1.1 200 OK\n"

    if (rash == 'css') or (rash == 'min'):
        CT = "Content-type: text/css\n"
    elif rash == 'html':
        CT = "Content-type: text/html\n"
    elif rash == 'png':
        CT = "Content-type: image/png\n"
    elif rash == 'jpeg':
        CT = "Content-type: image/jpeg\n"
    else:
        CT = "Content-type:\n"

    file = b''
    try:
        # if rash == 'png' or rash == 'jpeg':
        #     with open(msg, 'rb') as f:
        #         file = f.read()
        with open(os.path.join(config["dir"], msg), 'rb') as f:
            for line in f:
                file += line
    except FileNotFoundError:
        logging.info(f'{msg} - {addr[0]} - 404 NOT FOUND')
        status = "HTTP/1.1 404 NOT FOUND\n"
        with open(os.path.join(config["dir"], "404.html"), 'rb') as f:
            for line in f:
                file += line
    
    date = f'Date: {time.ctime()}\n'
    print(msg)

    resp = ""
    resp += status
    resp += f'Server: SelfMadeServer v0.0.1\n'
    resp += date
    resp += CT
    resp += f'Content-length: {len(file)}\n\n'
    resp = resp.encode() + file
    print(resp)
    resp += '\n\nConnection: close'.encode()
    

    conn.send(resp)

    conn.close()

while True:
    conn, addr = sock.accept()

    data = conn.recv(config["bite"])
    msg = data.decode()
    msg = msg.split(' ')[1]
    msg = msg[1:]

    if msg == 'favicon.ico':
        # Прошу прощения за этот костыль, так и не нашел откуда он пытается подгрузить favicon
        continue 

    if msg == '':
        msg = 'index.html'

    t1 = threading.Thread(target=work, args=[msg, conn, addr])
    t1.start()