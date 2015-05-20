from cvra_rpc.message import *
import cvra_rpc.service_call
from trajectory_publisher import *
from math import copysign
import time
import threading


TOLERANCE = 0.1
SETPOINT_FACTOR = 1.5

class HomingHandler:
    actuators = []

    def __init__(self, ip):
        self.ip = ip
        self.DESTINATION = (ip, 20001)
        self.pub = SimpleRPCActuatorPublisher((ip, 20000))

    class Actuator:
        def __init__(self, string_id):
            self.string_id = string_id
            self.got_first = False
            self.index_pos = 0
            self.pos_setpoint = 0
            self.pos_setpoint_set = False
            self.pos_setpoint_factor = 0.3
            self.stop = False


    def add(self, actuator_ids):
        for actuator_id in actuator_ids:
            self.actuators.append(self.Actuator(actuator_id))
            cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {actuator_id: {'stream': {'index': 10}}}}])
            cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {actuator_id: {'stream': {'motor_pos': 30}}}}])

    def index_callback(self, args):
        for actuator in self.actuators:
            if actuator.string_id == args[0]:
                if not actuator.stop:
                    if abs(args[1] - actuator.index_pos) >= TOLERANCE:
                        if not actuator.got_first:
                            actuator.index_pos = args[1]
                            actuator.got_first = True
                            actuator.pos_setpoint = actuator.index_pos + copysign(0.3, actuator.pos_setpoint - actuator.index_pos)
                            self.pub.update_actuator(actuator.string_id, PositionSetpoint(actuator.pos_setpoint))
                            self.pub.publish(time.time())
                        else:
                            actuator.stop = True
                            cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {actuator.string_id: {'stream': {'index': 0}}}}])
                            cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {actuator.string_id: {'stream': {'motor_pos': 0}}}}])
                            actuator.index_pos = (actuator.index_pos + args[1]) / 2
                            self.pub.update_actuator(actuator.string_id, PositionSetpoint(actuator.index_pos))
                            self.pub.publish(time.time())

    def pos_callback(self, args):
        for actuator in self.actuators:
            if actuator.string_id == args[0]:
                if not actuator.stop:
                    if not actuator.pos_setpoint_set:
                        actuator.pos_setpoint = args[1] + actuator.pos_setpoint_factor
                        self.pub.update_actuator(actuator.string_id, PositionSetpoint(actuator.pos_setpoint))
                        self.pub.publish(time.time())
                        actuator.pos_setpoint_set = True
                        actuator.pos_setpoint_factor *= -SETPOINT_FACTOR

                    else:
                        if abs(actuator.pos_setpoint - args[1]) <= TOLERANCE:
                            actuator.pos_setpoint = args[1] + actuator.pos_setpoint_factor
                            self.pub.update_actuator(actuator.string_id, PositionSetpoint(actuator.pos_setpoint))
                            self.pub.publish(time.time())
                            actuator.pos_setpoint_factor *= -SETPOINT_FACTOR

    def server_thread(self, server):
        server.serve_forever()
        return

    def start(self):
        TARGET = ('0.0.0.0', 20042)

        callbacks = {'position': self.pos_callback, 'index': self.index_callback}

        RequestHandler = create_request_handler(callbacks)
        server = socketserver.UDPServer(TARGET, RequestHandler)

        t = threading.Thread(target=self.server_thread, args=(server,))
        t.start()

        not_done = True

        while not_done:
            not_done = False
            for a in self.actuators:
                if not a.stop:
                    not_done = True

        server.shutdown()

        return {a.string_id: a.index_pos for a in self.actuators}
