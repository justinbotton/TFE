import sys
import time
import threading


class Affiche(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def typeCode(frame):
        tcHex = frame[8:10]
        tc = int(hex2bin(tcHex), 2)
        return tc

    def run(self):
        event = threading.Event()
        event.wait()
        q = self.queue
        ident = q.get(q.qsize())
        sys.stdout.write(ident + "\n")
        sys.stdout.flush()

    def hex2bin(frame):
        binary = "{0:08b}".format(int(frame, 16))
        output = binary[0:5]
        return output
