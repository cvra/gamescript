from cvra_rpc.service_call import call
from cvra_actuatorpub.trajectory_publisher import *
import time
import logging
from math import pi
import math
import argparse

YELLOW="yellow"
GREEN="green"

right_wheel_radius = 0.019
left_wheel_radius = 0.019
wheelbase = 0.155

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
                 'right-z':        [0.0, 0.0],
                 'right-shoulder': [0.0, 0.0],
                 'right-elbow':    [0.0, 0.0],
                 'right-wrist':    [0.0, 0.0],
                 'left-wheel':     0.,
                 'left-z':         [0.0, 0.0],
                 'left-shoulder':  [0.0, 0.0],
                 'left-elbow':     [0.0, 0.0],
                 'left-wrist':     [0.0, 0.0]}

    for actuator in actuators:
        logging.info('Creating actuator {}'.format(actuator))
        logging.info(create_actuator(args.host, actuator))

    # Find zero


    # Bras droit au corps (home)
    # move_arm('right', 0, -pi/2, pi/3, 0)
    # Bras gauche au corps (home)
    # move_arm('left', 0, -pi/2, pi/3, 0)
    # Avancer 500

    # Clap clap
    fwd(0.5); time.sleep(2.)
    turn(-90); time.sleep(2.)
    fwd(0.7); time.sleep(2.)
    turn(90); time.sleep(2.)
    fwd(0.1); time.sleep(2.)
    logging.warning("Moving arms here")
    fwd(0.1); time.sleep(2.)





    # Tourner -pi/2
    # turn_base(-pi/2)
    # Avancer 700
    # move_base(0.7)
    # Tourner pi/2
    # turn_base(pi/2)
    # Avancer 100
    # move_base(0.1)
    # Déployer bras droit à plat
    # move_arm('right', 0.2, -pi/2, pi/3, 0)
    # move_arm('right', 0.2, 0, 0, 0)
    # Avancer 200
    # move_base(0.2)
    # Bras droit au corps
    # move_arm('right', 0.2, -pi/2, pi/3, 0)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
