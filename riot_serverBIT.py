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
import subprocess
#from os.path import expanduser

from pythonosc import dispatcher
from pythonosc import osc_server
import netifaces

net_interface_type = "en0"
riot_ip = '192.168.1.100'
riot_ssid = 'riot'

class Utils:
    OS = None
    device_data = [""] # 1 json string for each device
    device_ids = [0]
    num_devices = len(device_ids)
    osc_server_started = False

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

def new_device(n):
    print ("new device connected!")
    ut.device_ids.append(n)
    ut.device_data.append("") #assign empty string to each device

def print_riot_data(unused_addr, *values):
    d_id = (int(unused_addr[1]))
    if d_id not in ut.device_ids:
        new_device(d_id)
    print("OSC Message %s from device %s" % (unused_addr, unused_addr[:2]))
    print(values)

def assign_riot_data(unused_addr, *values):
    d_id = (int(unused_addr[1]))
    if d_id not in ut.device_ids: new_device(d_id)

    channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    labels = ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X", "MAG_Y", "MAG_Z",
        "TEMP", "IO", "A1", "A2", "C", "Q1", "Q2", "Q3", "Q4", "PITCH", "YAW", "ROLL", "HEAD"]
    ch_mask = numpy.array(channels) - 1
    try:
        cols = numpy.arange(len(ch_mask))
        res = "{"
        for i in cols:
            res += '"' + labels[i] + '":' + str(values[i]) + ','
        res = res[:-1] + "}"
        #if len(cl) > 0: cl[-1].write_message(res)
        ut.device_data[d_id] = res
    except:
        traceback.print_exc()
        os._exit(0)

def assign_bitalino_data(unused_addr, *values):
    d_id = (int(unused_addr[1]))
    if d_id not in ut.device_ids: new_device(d_id)

    channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    labels = ["nSeq", "I1", "I2", "O1", "O2","A1","A2","A3","A4","A5","A6"]
    ch_mask = numpy.array(channels) - 1
    try:
        cols = numpy.arange(len(ch_mask))
        res = "{"
        for i in cols:
            res += '"' + labels[i] + '":' + str(values[i]) + ','
        res = res[:-1] + "}"
        #if len(cl) > 0: cl[-1].write_message(res)
        ut.device_data[d_id] = res
    except:
        traceback.print_exc()
        os._exit(0)

def riot_listener(ip, port):
#    for d_id in ut.device_ids:
#        recv_addr = str("/%i/raw"%d_id)
#        riot_dispatcher = dispatcher.Dispatcher()
#        riot_dispatcher.map(recv_addr, assign_riot_data)

    riot_dispatcher = dispatcher.Dispatcher()
    riot_dispatcher.map("/*/raw", assign_riot_data)
    # riot_dispatcher.map("/*/bitalino", assign_bitalino_data)

    # server = osc_server.ThreadingOSCUDPServer(
    #   (ip, port), riot_dispatcher)
    server = osc_server.ThreadingOSCUDPServer(
      (ip, port), riot_dispatcher)
    print("Serving on {}".format(server.server_address))
    ut.osc_server_started = True
    server.serve_forever()

def detect_net_config(net_interface_type, OS):
    if net_interface_type is not None:
        net_interface_type, ssid = detect_wireless_interface([net_interface_type], OS)
    while net_interface_type is None:
        try:
            print ("detecting wireless interface... (this can be set manually with --net)")
            net_interface_type, ssid = detect_wireless_interface(OS, netifaces.interfaces())
            print("Connected to wifi network: " + str(ssid))
        except Exception as e:
            print(e)
            print ("could not retrieve ssid from %s" % net_interface_type)
            print ("see available interfaces with: \n \
                ifconfig -a (UNIX) \n ipconfig |findstr 'adapter' (WINDOWS)")
            print ('{:^24s}'.format("====================="))
            input ("please connect to a Wi-Fi network and press ENTER to continue")
    return net_interface_type, ssid

def detect_wireless_interface(interface_list, OS):
    det_interface = det_ssid = None
    for interface in interface_list:
        if ("linux" in OS or "Linux" in OS):
            det_interface = os.popen('iwgetid').read()[:-1].split()[0]
            det_ssid = os.popen('iwgetid -r').read()[:-1]
            break
        elif ("Windows" in OS):
            det_interface = os.popen('netsh wlan show interfaces | findstr /r "^....Name"').read()[:-1].split()[-1]
            det_ssid = os.popen('netsh wlan show interfaces | findstr /r "^....SSID"').read()[:-1].split()[-1]
            break
        else:
            ssid = os.popen('networksetup -getairportnetwork ' + interface).read()[:-1]
            print(ssid)
            if '** Error: Error obtaining wireless information' not in ssid:
                det_ssid = ssid[23:]
                det_interface = interface
                break
    return det_interface, det_ssid

def detect_ipv4_address(net_interface_type, OS):
    if "Windows" in OS:
            ipv4_addr = os.popen('netsh interface ipv4 show config %s | findstr /r "^....IP Address"' % net_interface_type).read()[:-1].split()[-1]
            print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))
    else:
        addrs = netifaces.ifaddresses(net_interface_type)
        ipv4_addr = addrs[netifaces.AF_INET][0]['addr']
        print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))
    return ipv4_addr

def reconfigure_ipv4_address(riot_ip, ipv4_addr, OS):
    if riot_ip not in ipv4_addr:
        print ("The computer's IPv4 address must be changed to match")
        if "Windows" in OS:
            cmd = "netsh interface ip set address %s static %s 255.255.255.0 192.168.1.1" % (net_interface_type, args.ip)
            input("press ENTER to auto re-configure network settings and continue. You may need to re-open R-IoT serverBIT")
            try:
                proc = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                timer(3)
                return
            except subprocess.CalledProcessError:
                input ("There was an error, please run as administrator. You can also change the ipv4 address manually (see R-IoT guide)  \
                \nclose window and try again")
                sys.exit(1)
        else:
            # UNIX ifconfig command with sudo
            cmd = '"sudo ifconfig %s %s netmask 255.255.255.0"' % (net_interface_type, riot_ip)
            if "Linix" in OS:
                # to run command from terminal, will promt for sudo password
                print(">>> paste the following command: ")
                print ( cmd )
                input("OR press ENTER to auto re-configure network settings and continue. You may need to re-open R-IoT serverBIT")
            else:
                # request OSX root privilege with GUI promt
                cmd = "osascript -e 'do shell script %s with prompt %s with administrator privileges'" % (cmd, '"ServerBIT requires root access."')
            try:
                # wait unitl command has run before continuing
                proc = subprocess.check_output(cmd, shell=True)
                timer(3)
                return
            except subprocess.CalledProcessError:
                print(cmd)
                input ("There was an error running this command. You can also change the ipv4 address manually (see R-IoT guide)  \
                \nclose window and try again")
                sys.exit(1)

def update_progress(count, total, status=''):
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
def timer(t, rate = 0.25, text=''):
    tt=round((t+rate)/rate)
    for i in range(tt):
        update_progress(i, round(t/rate), text)
        time.sleep(rate)
    print("\n")

def reset():
    time.sleep(0.5)
    os.execl(sys.executable, os.path.abspath(_file_), *sys.argv)

async def webApp(ws, path):
#    device_id = ws.port - 9001
    print('LISTENING')
#    print (ut.device_data[device_id])
    # ws_path_id = path[-1]
    while ut.device_data[0] != "":
        await ws.send(ut.device_data[0])
        await asyncio.sleep(0.1)
    # for device_id in ut.device_ids:
    #     if True:
    #     # if ws_path_id.isdigit() and int(ws_path_id) == device_id:
    #         try:
    #             print ("streaming data from device %i to  ws://%s:%i%s" % (device_id, ws.host, ws.port, path))
    #             while ut.device_data[device_id] != "":
    #                 await ws.send(ut.device_data[device_id])
    #                 await asyncio.sleep(0.1)
    #         except:
    #             pass

if __name__ == "__main__":
    # -1- parse arguemnts
    OS = platform.system()
    parser = argparse.ArgumentParser()
    parser.add_argument("--id",
      type=int, default=0, help="This dictates the OSC reveive address: /<id>/raw")
    parser.add_argument("--ip",
      default=riot_ip, help="The ip to listen on (usually set to 192.168.1.00)")
    parser.add_argument("--port",
      type=int, default=8888, help="The port to listen on")
    parser.add_argument("--ssid",
      default=riot_ssid, help="name of the wifi network which R-IoT device is streaming data to")
    parser.add_argument("--net_interface",
      default=None, help="name of the wireless interface which the computer is using")
    parser.add_argument("--websockets_ip",
      default='127.0.0.1', help="destination ip for websocket handler")
    parser.add_argument("--websockets_port",
      type=int, default=9001, help="destination port for websocket handler is the port + device ID")
    parser.add_argument("--find_new",
      type=int, default=1, help="find new devices in network")
    args = parser.parse_args()

    # -2- network config
    # -2.1- get network interface and ssid & assign module ip
#    net_interface_type, ssid = detect_net_config(args.net_interface, OS)

    # -2.2- get serverBIT host ipv4 address
#    ipv4_addr = detect_ipv4_address(net_interface_type, OS)

    # -2.3- check host ssid matches that assigned to the R-IoT module
#    while ssid not in args.ssid:
#        print ('{:^24s}'.format("====================="))
#        print ("currently connected to '%s', please connect to the same network as the R-IoT (%s)" % (ssid, args.ssid))
##        print ("(target ssid can be changed with --ssid 'name_of_network')")
#        input("please re-open R-IoT_ServerBIT or press ENTER to retry")
#        # update network properties
#        net_interface_type, ssid = detect_net_config(args.net_interface, OS)

    # -2.4- change host ipv4 to match the R-IoT module if required
    if riot_ip not in args.ip:
        print ("IP address changed from R-IoT default (%s)" % riot_ip)
#    reconfigure_ipv4_address(args.ip, ipv4_addr, OS)

    print ("Starting riot_serverBIT...")
    timer(2)

    # -3- stream device data to network
    try:
        thread.start_new_thread(riot_listener, (args.ip, args.port)) # one thread to listen to all devices on the same ip & port
        while not ut.osc_server_started : time.sleep(0.1)
        if args.find_new == 1: timer(5, text="searching for devices on this network")
        while ut.device_data[0] == "" or len(ut.device_ids) == 0:
            print ("no devices found")
            timer(5, text="searching for devices on this network")
        print ("found %i device(s)" % len(ut.device_ids))
        start_server = websockets.serve(webApp, args.websockets_ip, args.websockets_port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print (e)
    finally:
        print ()
        sys.exit(1)
