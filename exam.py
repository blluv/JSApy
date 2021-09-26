from jsa import JSA
import time

jsa = JSA()
jsa.connect("COM11")
c = False
while True:
    if jsa.getData().getInputPorts()[3]["val"] == 0:
        if c:
            jsa.setServo(180)
            c=False
    else:
        c=True
        jsa.setServo(0)
    time.sleep(2/1000)