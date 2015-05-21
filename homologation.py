from cvra_rpc.service_call import *

from cvra_actuatorpub.trajectory_publisher import *
import time
import logging
from math import pi
import math
import argparse
from threading import Thread, Event
from master_board import leds
import socketserver

YELLOW="yellow"
GREEN="green"

right_wheel_radius = 0.019
left_wheel_radius = 0.019
wheelbase = 0.155
game_start_event = Event()


def move_base(distance, pub, actuators):
    logging.info('Moving {}'.format(distance))
    actuators['right-wheel'] += distance / right_wheel_radius
    actuators['left-wheel'] += distance / left_wheel_radius
    pub.update_actuator('right-wheel', PositionSetpoint(actuators['right-wheel']))
    pub.update_actuator('left-wheel', PositionSetpoint(actuators['left-wheel']))
    pub.publish(time.time())

def turn_base(angle, pub, actuators):
    logging.info('Turning {}'.format(math.degrees(angle)))
    actuators['right-wheel'] += angle * (wheelbase / 2) / right_wheel_radius
    actuators['left-wheel'] += - angle * (wheelbase / 2) / left_wheel_radius
    pub.update_actuator('right-wheel', PositionSetpoint(actuators['right-wheel']))
    pub.update_actuator('left-wheel', PositionSetpoint(actuators['left-wheel']))
    pub.publish(time.time())



def move_arm(flip, z, shoulder, elbow, wrist, pub, actuators):
    actuators[flip + '-z'][0] = z
    actuators[flip + '-shoulder'][0] = shoulder
    actuators[flip + '-elbow'][0] = elbow
    actuators[flip + '-wrist'][0] = wrist
    pub.update_actuator(flip + '-z', PositionSetpoint(actuators[flip + '-z'][0]))
    pub.update_actuator(flip + '-shoulder', PositionSetpoint(actuators[flip + '-shoulder'][0]))
    pub.update_actuator(flip + '-elbow', PositionSetpoint(actuators[flip + '-elbow'][0]))
    pub.update_actuator(flip + '-wrist', PositionSetpoint(actuators[flip + '-wrist'][0]))
    pub.publish(time.time())

def create_actuator(host, name):
    return call((host, 20001), 'actuator_create_driver', [name])

def parse_cmdline():
    parser = argparse.ArgumentParser('Ugly homologation script')
    parser.add_argument('host', help="Master board IP")
    parser.add_argument('color', choices=[YELLOW, GREEN])
    return parser.parse_args()

def main():
    args = parse_cmdline()

    pub = SimpleRPCActuatorPublisher((args.host, 20000))

    def fwd(x):
        move_base(x, pub, actuators)

    def turn(x):
        if args.color == YELLOW:
            turn_base(math.radians(x), pub, actuators)
        else:
            turn_base(-math.radians(x), pub, actuators)


    # First value is position, second value is index
    actuators = {'right-wheel':    0.,
#                 'right-z':        [0.0, 0.0],
#                 'right-shoulder': [0.0, 0.0],
#                 'right-elbow':    [0.0, 0.0],
#                 'right-wrist':    [0.0, 0.0],
                 'left-wheel':     0.,
#                 'left-z':         [0.0, 0.0],
#                 'left-shoulder':  [0.0, 0.0],
#                 'left-elbow':     [0.0, 0.0],
#                 'left-wrist':     [0.0, 0.0]}
}

    for actuator in actuators:
        logging.info('Creating actuator {}'.format(actuator))
        logging.info(create_actuator(args.host, actuator))

    # Find zero
    logging.warning("Not implemented yet: find zeroes")

    logging.info("Waiting for start...")

    leds.set_led((args.host, 20001), leds.Led.Ready, True)
    game_start_event.wait()
    logging.info("Starting!")

    # Clap clap
    fwd(0.5); time.sleep(2.)
    turn(-90); time.sleep(2.)
    fwd(0.7); time.sleep(2.)
    turn(90); time.sleep(2.)
    fwd(0.1); time.sleep(2.)
    logging.warning("Moving arms here")
    fwd(0.1); time.sleep(2.)



def button_released(args):
    logging.info("Button {} release".format(args))
    if args[0] == 'start':
        logging.debug("Setting start event")
        game_start_event.set()

def button_pressed(args):
    logging.info("Button {} press".format(args))


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

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    Thread(target=interface_thread).start()
    main()
