from cvra_rpc.service_call import *
import argparse
from cvra_actuatorpub.trajectory_publisher import *
import time
import socketserver
from threading import Thread, Event
from cvra_actuatorpub.trajectory_publisher import *

HOST = 'debra-master'

running = True


def create_actuator(name):
    return call((HOST, 20001), 'actuator_create_driver', [name])

def button_released(args):
    logging.info("Button {} press".format(args))
    pass

def button_pressed(args):
    global running
    logging.info("Button {} release".format(args))

    if args[0] == 'yellow':
        running = False
    else:
        running = True

    logging.info("Running {}".format(running))

def interface_thread():
    logging.info("Starting interface panel thread")
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    callbacks = {
            'button_released':button_released,
            'button_pressed':button_pressed
    }

    try:
        MyTCPHandler = create_request_handler(callbacks)
        server = socketserver.TCPServer(('0.0.0.0', 20002), MyTCPHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        logging.error("Received Ctrl-c exiting cleanly...")
        server.shutdown()

Thread(target=interface_thread).start()

parser = argparse.ArgumentParser()
parser.add_argument('host')
parser.add_argument('value', type=float)
parser.add_argument('--actuator', '-a',  default='foobar2000',
                    help="Actuator to set (default foobar2000)")

parser.add_argument('--negative', '-n', action='store_true')
parser.add_argument('--create', '-c', action='store_true')
parser.add_argument('--position', '-p', action='store_true')
parser.add_argument('--speed', '-s', action='store_true')
parser.add_argument('--torque', '-t', action='store_true')

args = parser.parse_args()

print(create_actuator('right-shoulder'))
print(create_actuator('right-elbow'))
print(create_actuator('right-wrist'))
print(create_actuator('right-wheel'))
print(create_actuator('left-wheel'))

pub = SimpleRPCActuatorPublisher((args.host, 20000))

logging.getLogger().setLevel(logging.DEBUG)


pub.update_actuator('right-wheel', PositionSetpoint(0.))
pub.update_actuator('left-wheel', PositionSetpoint(0.))
while True:
    if running:
        pub.update_actuator('right-shoulder', PositionSetpoint(1.))
        pub.update_actuator('right-elbow', PositionSetpoint(-1.))
        pub.update_actuator('right-wrist', SpeedSetpoint(1.))
        pub.publish(time.time())

        time.sleep(2.)

        pub.update_actuator('right-shoulder', PositionSetpoint(-1.))
        pub.update_actuator('right-elbow', PositionSetpoint(1.))
        pub.publish(time.time())

        time.sleep(2.)
    else:
        pub.update_actuator('right-wrist', SpeedSetpoint(0.))
        pub.publish(time.time())
        time.sleep(0.1)
