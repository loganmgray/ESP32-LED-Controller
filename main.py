import wifimgr
import server
import control
import socket
import ure


wlan = wifimgr.get_connection()
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D


# Main Code goes here, wlan is a working network.WLAN(STA_IF) instance.
print("ESP OK")
controller = control.LEDController()
server.serve(wlan, controller)
