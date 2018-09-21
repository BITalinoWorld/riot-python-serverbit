""" OSC server ofr BITalino R-IoT

"""
import argparse
import math

from tornado import websocket, web, ioloop
import _thread as thread
import asyncio
import websockets
import json
import signal
import numpy
import sys, traceback, os, time, platform
#from os.path import expanduser

from pythonosc import dispatcher
from pythonosc import osc_server
import netifaces

net_interface_type = "wlp5s0"
riot_ip = '192.168.1.100'
riot_ssid = 'riot'

class Utils:
    OS = None
    riot_data = ""

ut = Utils()

def printJSON(decoded_json_input):
    try:
        # pretty printing of json-formatted string
        print (json.dumps(decoded_json_input, sort_keys=True , indent=4))
    except (ValueError, KeyError, TypeError):
        print ("JSON format error")

def tostring(data):
    """
    :param data: object to be converted into a JSON-compatible `str`
    :type data: any
    :return: JSON-compatible `str` version of `data`

    Converts `data` from its native data type to a JSON-compatible `str`.
    """
    dtype = type(data).__name__
    if dtype == 'ndarray':
        if numpy.shape(data) != ():
            data = data.tolist()  # data=list(data)
        else:
            data = '"' + data.tostring() + '"'
    elif dtype == 'dict' or dtype == 'tuple':
        try:
            data = json.dumps(data)
        except:
            pass
    elif dtype == 'NoneType':
        data = ''
    elif dtype == 'str' or dtype == 'unicode':
        data = json.dumps(data)

    return str(data)

def print_riot_data(unused_addr, id, *values):
  print("OSC Message %s from device %s" % (unused_addr, id[0]))
  print(values)

def assign_riot_data(unused_addr, id, *values):
    channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    labels = ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X", "MAG_Y", "MAG_Z",
        "TEMP", "IO", "A1", "A2", "Q1", "Q2", "Q3", "Q4", "PITCH", "YAW", "ROLL", "HEAD",]
    ch_mask = numpy.array(channels) - 1
    try:
        cols = numpy.arange(len(ch_mask))
        res = "{"
        for i in cols:
            res += '"' + labels[i] + '":' + str(values[i]) + ','
        res = res[:-1] + "}"
        #if len(cl) > 0: cl[-1].write_message(res)
        ut.riot_data = res
        #print (res)
    except:
        traceback.print_exc()
        os._exit(0)

def riot_listener(id, ip, port):
    dev_id = id
    recv_addr = str("/%i/raw"%dev_id)
    #print(recv_addr)
    riot_dispatcher = dispatcher.Dispatcher()
    #riot_dispatcher.map(recv_addr, print_riot_data, dev_id)
    riot_dispatcher.map(recv_addr, assign_riot_data, dev_id)

    server = osc_server.ThreadingOSCUDPServer(
      (ip, port), riot_dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

async def webApp(ws, path):
    print('LISTENING')
    #print (ut.riot_data)
    while True:
        await ws.send(ut.riot_data)
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    OS = platform.system()
    for interface in netifaces.interfaces():
        ssid = os.popen('iwconfig ' + interface + ' | grep '+ "'ESSID:' | awk '{print $4}' | sed 's/ESSID://g' | sed 's/"+ '"//g' + "'").read()[:-1]
        if 'no wireless extention' not in ssid:
            net_interface_type = interface
    addrs = netifaces.ifaddresses(net_interface_type)
    ssid = os.popen('iwconfig wlp5s0 | grep '+ "'ESSID:' | awk '{print $4}' | sed 's/ESSID://g' | sed 's/"+ '"//g' + "'").read()[:-1]
    print("Connected to wifi network: " + ssid)
    ipv4_addr = addrs[netifaces.AF_INET][0]['addr']
    print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))

    parser = argparse.ArgumentParser()
    parser.add_argument("--id",
      type=int, default=0, help="This dictates the OSC reveive address: /<id>/raw")
    parser.add_argument("--ip",
      default=riot_ip, help="The ip to listen on (usually set to 192.168.1.00)")
    parser.add_argument("--port",
      type=int, default=8888, help="The port to listen on")
    parser.add_argument("--ssid",
      default=riot_ssid, help="name of the wifi network which R-IoT device is streaming data to")
    args = parser.parse_args()

    if riot_ip not in args.ip:
        print ("IP address changed from R-IoT default (%s)" % riot_ip)

    if ssid not in args.ssid:
        print ("currently connected to '%s', please connect to the same network as the R-IoT" % ssid)
        print ("target ssid can be changed with --ssid 'name_of_network'")
        exit()

    if args.ip not in ipv4_addr:
        print ("please change the computer's IPv4 address to match")
        exit()
    try:
        thread.start_new_thread(riot_listener, (args.id, args.ip, args.port))
        start_server = websockets.serve(webApp, '127.0.0.1', 9001)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        # ioloop.IOLoop.instance().start()
    finally:
        sys.exit(1)
