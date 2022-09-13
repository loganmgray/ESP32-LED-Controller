import machine

class LEDController:

    def __init__(self):
        self._channels = [machine.PWM(machine.Pin(25)), 
                          machine.PWM(machine.Pin(26)), 
                          machine.PWM(machine.Pin(27))]

    def act(self, color: int):
        #color is 0xrrggbb format
        rgb = [color >> 16 & 0xff,
               color >> 8 & 0xff,
               color & 0xff]
        duties = []
        for i, clr in enumerate(rgb):
            self._channels[i].duty(clr*4)
            duties.append(self._channels[i].duty())
        print(duties)

