# Optional arguments

- `"--id"`: This dictates the OSC reveive address (/<id>/raw). change this if using multiple devices
- `"--ip"`: The ip to listen on (usually set to 192.168.1.00)
- `"--port"`: The ip to listen on (usually set to 8888)
- `"--ssid"`: name of the wifi network which R-IoT device is streaming data to

**If you are using a pre-configured TP-LINK router, you should not need to change these**

For more information, please see the R-IoT guide:
[R-IoT_User_Guide.pdf](http://www.bitalino.com/docs/R-IoT_User_Guide.pdf)

### Windows
Set IPv4 address, netmask and gateway:
netsh interface ip set address Wi-Fi static 192.168.1.100 255.255.255.0 192.168.1.1

To get back online, reset dhcp:
netsh interface ip set address Wi-Fi dhcp




