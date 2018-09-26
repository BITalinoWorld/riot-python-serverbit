netsh interface ip set address Wi-Fi dhcp
@echo reset ipv4 to dhcp
TIMEOUT 3
netsh wlan disconnect
@echo disconnecting Wi-Fi
pause
