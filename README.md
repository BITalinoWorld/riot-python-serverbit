# R-IoT ServerBIT
This can be used to forward the R-IoT's OSC messages to WebSockets. We've also provided some handy tools for setting up your computer's network to work with the device.

For more information for getting started with the R-IoT, please see the guide:
[R-IoT_User_Guide.pdf](http://www.bitalino.com/docs/R-IoT_User_Guide.pdf)

### Optional arguments

- `"--id"`: This dictates the OSC reveive address (/<id>/raw). change this if using multiple devices
- `"--ip"`: The ip to listen on (usually set to 192.168.1.00)
- `"--port"`: The ip to listen on (usually set to 8888)
- `"--ssid"`: name of the wifi network which R-IoT device is streaming data to

additional arguments can be viewed using the -h flag

*If you are using a pre-configured TP-LINK router, you should not need to change these. Otherwise, follow the steps below*

### Changing the default configuration
This program assumes the default configuration of the device. If these settings are changed, it's required to parse the new settings to the script

##### Configuration page
To change the default configuration, see **R-IoT configuration & setup -> Changing the default configuration** in the [user guide](http://www.bitalino.com/docs/R-IoT_User_Guide.pdf)

![riot_ServerBIT_config1](https://gitlab.com/weselle/riot-serverbit/uploads/1eb0f685cdf526b8304ba4eeaa6b296f/riot_ServerBIT_config1.png)

Run script with arguments

```
$ python3 riot_serverBIT.py -ssid 'riot' --ip '192.168.1.100' --port 8888 --id 0
```

or edit [start_win64.bat](start_win64.bat)

```
"python_win64\python.exe" "riot_serverBIT.py -ssid 'riot' --ip '192.168.1.100' --port 8888 --id 0"
```

### Getting started (threejs example)
1. With router switched on, Turn on the R-IoT device

![ezgif-3-83cdbcc833](https://gitlab.com/weselle/riot-serverbit/uploads/86701a1974414c543b67701f6176ab8d/ezgif-3-83cdbcc833.gif)

2. Connct to Wi-Fi network

![Screenshot__6_](https://gitlab.com/weselle/riot-serverbit/uploads/54ee41c423e08e42fa197e6f74df426b/Screenshot__6_.png)

3. Run riot_serverBIT.py

```
python3 riot_serverBIT.py
```
4. Accept auto configuration or run the given command. Re-launch riot_serverBIT if needed

![C__WINDOWS_System32_cmd.exe_9_26_2018_3_04_40_PM](https://gitlab.com/weselle/riot-serverbit/uploads/909f6b52e6407506ac218a1929e59f1d/C__WINDOWS_System32_cmd.exe_9_26_2018_3_04_40_PM.png)

5. Server is now running, open [/riot_threejs_example/riot_threejs_example.html](/riot_threejs_example/riot_threejs_example.html) (if already open, refresh page)
 
![ezgif-3-8d48ccf9a2](https://gitlab.com/weselle/riot-serverbit/uploads/95340dac2a712c2efe8adb890e131560/ezgif-3-8d48ccf9a2.gif)

### Windows Commands
Manually set IPv4 address, netmask and gateway:

```
netsh interface ip set address Wi-Fi static 192.168.1.100 255.255.255.0 192.168.1.1
```


To get back online, reset dhcp (run as admin):

```
netsh interface ip set address Wi-Fi dhcp
```

### No router? Setting up a direct Wi-Fi connection using Access Point mode

By enabling Access Point mode, you'll be able to connect to the R-IoT's wireless network directly. From here, the sensor data will stream to an OSC server on your device. You can initiate this connection using ServerBIT.

For more information, please have a look at this tutorial: [https://serverbit.gitbook.io/docs/r-iot/no-router-setting-up-a-direct-wi-fi-connection-using-access-point-mode](https://serverbit.gitbook.io/docs/r-iot/no-router-setting-up-a-direct-wi-fi-connection-using-access-point-mode)
