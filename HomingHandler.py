from cvra_rpc.message import *
import cvra_rpc.service_call
from trajectory_publisher import *
from math import copysign
import time
import threading


TOLERANCE = 0.1
SETPOINT_FACTOR = 1.5

class HomeZ:
    actuators = []

    def __init__(self, ip):
        self.ip = ip
        self.DESTINATION = (ip, 20001)
        self.pub = SimpleRPCActuatorPublisher((ip, 20000))

    class Actuator:
        def __init__(self, string_id, velocity_setpt, torque_min_max):
            self.string_id = string_id
            self.zero = 0
            self.velocity = 0
            self.velocity_setpt = velocity_setpt
            self.torque_min_max = torque_min_max
            self.was_fast = False
            self.stop = False


    def add(self, actuator_ids, velocity_setpt, torque_min_max):
        for actuator_id in actuator_ids:
            self.actuators.append(self.Actuator(actuator_id, velocity_setpt, torque_min_max))

    def pos_callback(self, args):
        for actuator in self.actuators:
            if actuator.string_id == args[0]:
                if not actuator.stop:
                    if actuator.was_fast and args[2] < actuator.velocity_setpt * 0.1 and abs(args[2]) < abs(actuator.velocity):   # if actual velocity is < 10% of setpoint
                        print(args[2])
                        print(actuator.velocity)
                        actuator.zero = args[1]
                        self.pub.update_actuator(actuator.string_id, SpeedSetpoint(float(0)))
                        self.pub.publish(time.time())
                        cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {actuator.string_id: {'stream': {'motor_pos': 0}}}}])
                        cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {actuator.string_id: {'control': {'torque_limit': min(actuator.torque_min_max)}}}}])
                        actuator.stop = True
                    actuator.velocity = args[2]
                    if actuator.velocity > 0.1 * actuator.velocity_setpt:
                        actuator.was_fast = True

    def server_thread(self, server):
        server.serve_forever()
        return

    def start(self):
        TARGET = ('0.0.0.0', 20042)

        callbacks = {'position': self.pos_callback}

        RequestHandler = create_request_handler(callbacks)
        server = socketserver.UDPServer(TARGET, RequestHandler)

        t = threading.Thread(target=self.server_thread, args=(server,))
        t.start()

        for a in self.actuators:
            cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {a.string_id: {'stream': {'motor_pos': 100}}}}])
            cvra_rpc.service_call.call(self.DESTINATION, 'config_update', [{'actuator': {a.string_id: {'control': {'torque_limit': min(a.torque_min_max)}}}}])
            self.pub.update_actuator(a.string_id, SpeedSetpoint(a.velocity_setpt))
            self.pub.publish(time.time())

        not_done = True

        while not_done:
            not_done = False
            for a in self.actuators:
                if not a.stop:
                    not_done = True

        server.shutdown()

        return {a.string_id: a.zero for a in self.actuators}


class Indexer:
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
