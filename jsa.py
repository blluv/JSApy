import serial

sensor_type = {
    0: "DISCONNECTED",
    1: "LIGHT",
    2: "IR",
    3: "TOUCH",
    4: "POTENTIOMETER",
    5: "MIC",
    6: "ULTRASONIC",
    7: "TEMPERATURE",
    10: "VIBRATION",
    11: "EXTENSION",
    20: "LED",
    19: "SERVO",
    18: "DC_MOTOR",
}


class Frame():
    def_frame = [255, 255, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 254, 254]

    inputPorts = [2, 4, 6, 8]

    outputReadPorts = [10, 11]
    outputWritePorts = [5, 7]

    def __init__(self, data=def_frame.copy()):
        self.data = data

    def reset(self):
        self.data = self.def_frame.copy()

    def setBuzzer(self, val):
        self.data[3] = max(0, min(96, val) - 11)

    def setLED(self, r, g, b):
        self.data[13] = min(max(r, 0), 255)
        self.data[15] = min(max(g, 0), 255)
        self.data[17] = min(max(b, 0), 255)

    def setServo(self, port, val):
        val = max(0, min(180, val))
        val = 180 - val + 1
        self.data[self.outputWritePorts[self.outputReadPorts.index(
            port)]] = val

    def getInputPort(self, port):
        if not port in self.inputPorts:
            raise Exception("Invalid Port")

        type = sensor_type[self.data[port] >> 2]
        val = (self.data[port] & 3) << 8 | self.data[port + 1]

        if type == "TEMPERATURE":
            val = self._convTemp(val)

        return {
            "type": type,
            "port": port,
            "val": val,
        }

    def getOutputPort(self, port):
        if not port in self.outputReadPorts:
            raise Exception("Invalid Port")

        type = sensor_type[self.data[port] & 127]

        return {
            "type": type,
            "port": port
        }

    def getInputPorts(self):
        ports = []
        for port in self.inputPorts:
            ports.append(self.getInputPort(port))
        return ports

    def getOutputPorts(self):
        ports = []
        for port in self.outputReadPorts:
            ports.append(self.getOutputPort(port))
        return ports

    def _convTemp(self, val):
        a = val - 40
        if a < -40:
            a = -40
        elif a > 120:
            a = 120
        return a

    def getBytes(self):
        return bytes(self.data)


class JSA():
    device: serial.Serial
    frame: Frame

    def __init__(self):
        pass

    def connect(self, serial_port):
        self.frame = Frame()
        self.device = serial.Serial(
            serial_port, 38400, parity="N", bytesize=8, stopbits=1)
        self.getData()
        return self.device.isOpen()

    def _readFrame(self):
        data = self.device.read(size=17)
        frame = Frame(data)
        return frame

    def getData(self):
        if self.device.isOpen():
            self.device.write(bytes(self.frame.getBytes()))
            return self._readFrame()
        else:
            raise Exception("disconnected")

    def setBuzzer(self, val):
        self.frame.setBuzzer(val)
        self.device.write(self.frame.getBytes())
        self.frame.setBuzzer(0)
        self._readFrame()

    def setLED(self, r, g, b):
        self.frame.setLED(r, g, b)
        self.device.write(self.frame.getBytes())
        self._readFrame()

    def setServo(self, val):
        ports = self.getData().getOutputPorts()
        for port in ports:
            if port["type"] == "SERVO":
                self.frame.setServo(port["port"], val)
                self.device.write(self.frame.getBytes())
                self._readFrame()
