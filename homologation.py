from cvra_rpc.service_call import call
from cvra_actuatorpub.trajectory_publisher import *
import time

HOST = '192.168.3.20'

def move_base(distance):
    global pub, actuators
    actuators['right-wheel'][0] += distance / (2 * pi * right-wheel-radius)
    actuators['left-wheel'][0] += distance / (2 * pi * left-wheel-radius)
    pub.update_actuator('right-wheel', PositionSetpoint(actuators['right-wheel'][0] + actuators['right-wheel'][1]))
    pub.update_actuator('left-wheel', PositionSetpoint(actuators['left-wheel'][0] + actuators['left-wheel'][0]))
    pub.publish(time.time())

def turn_base(angle):
    global pub, actuators
    actuators['right-wheel'][0] += angle * wheelbase / (2 * pi * right-wheel-radius)
    actuators['left-wheel'][0] += - angle * wheelbase / (2 * pi * left-wheel-radius)
    pub.update_actuator('right-wheel', PositionSetpoint(actuators['right-wheel'][0] + actuators['right-wheel'][1]))
    pub.update_actuator('left-wheel', PositionSetpoint(actuators['left-wheel'][0] + actuators['left-wheel'][0]))
    pub.publish(time.time())

def move_arm(flip, z, shoulder, elbow, wrist):
    global pub, actuators
    actuators[flip + '-z'][0] = z
    actuators[flip + '-shoulder'][0] = shoulder
    actuators[flip + '-elbow'][0] = elbow
    actuators[flip + '-wrist'][0] = wrist
    pub.update_actuator(flip + '-z', PositionSetpoint(actuators[flip + '-z'][0]))
    pub.update_actuator(flip + '-shoulder', PositionSetpoint(actuators[flip + '-shoulder'][0]))
    pub.update_actuator(flip + '-elbow', PositionSetpoint(actuators[flip + '-elbow'][0]))
    pub.update_actuator(flip + '-wrist', PositionSetpoint(actuators[flip + '-wrist'][0]))
    pub.publish(time.time())

def create_actuator(name):
    return call((HOST, 20001), 'actuator_create_driver', [name])

def main():
    global pub, actuators
    pub = SimpleRPCActuatorPublisher((HOST, 20000))

    # First value is position, second value is index
    actuators = {'right-wheel':    [0.0, 0.0],
                 'right-z':        [0.0, 0.0],
                 'right-shoulder': [0.0, 0.0],
                 'right-elbow':    [0.0, 0.0],
                 'right-wrist':    [0.0, 0.0],
                 'left-wheel':     [0.0, 0.0],
                 'left-z':         [0.0, 0.0],
                 'left-shoulder':  [0.0, 0.0],
                 'left-elbow':     [0.0, 0.0],
                 'left-wrist':     [0.0, 0.0]}

    for actuator in actuators:
        print(create_actuator(actuator))

    # Find zero


    # Bras droit au corps (home)
    move_arm('right', 0, -pi/2, pi/3, 0)
    # Bras gauche au corps (home)
    move_arm('left', 0, -pi/2, pi/3, 0)
    # Avancer 500
    move_base(0.5)
    # Tourner -pi/2
    turn_base(-pi/2)
    # Avancer 700
    move_base(0.7)
    # Tourner pi/2
    turn_base(pi/2)
    # Avancer 100
    move_base(0.1)
    # Déployer bras droit à plat
    move_arm('right', 0.2, -pi/2, pi/3, 0)
    move_arm('right', 0.2, 0, 0, 0)
    # Avancer 200
    move_base(0.2)
    # Bras droit au corps
    move_arm('right', 0.2, -pi/2, pi/3, 0)

if __name__ == "__main__":
    main()
