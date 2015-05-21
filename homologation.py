from cvra_rpc.service_call import call
from cvra_actuatorpub.trajectory_publisher import *
import time

HOST = '192.168.3.20'

def move_base(distance):
    global pub
    pub.update_actuator('right-wheel', PositionSetpoint(distance / (2 * pi * right-wheel-radius)))
    pub.update_actuator('left-wheel', PositionSetpoint(distance / (2 * pi * left-wheel-radius)))
    pub.publish(time.time())

def turn_base(angle):
    global pub
    pub.update_actuator('right-wheel', PositionSetpoint(angle * wheelbase / (2 * pi * right-wheel-radius)))
    pub.update_actuator('left-wheel', PositionSetpoint(- angle * wheelbase / (2 * pi * left-wheel-radius)))
    pub.publish(time.time())

def move_arm(flip, z, shoulder, elbow, wrist):
    global pub
    pub.update_actuator(flip+'-z', PositionSetpoint(z))
    pub.update_actuator(flip+'-shoulder', PositionSetpoint(shoulder))
    pub.update_actuator(flip+'-elbow', PositionSetpoint(elbow))
    pub.update_actuator(flip+'-wrist', PositionSetpoint(wrist))
    pub.publish(time.time())

def create_actuator(name):
    return call((HOST, 20001), 'actuator_create_driver', [name])

def main():
    global pub
    pub = SimpleRPCActuatorPublisher((HOST, 20000))

    actuators = ['right-wheel',
                 'right-z',
                 'right-shoulder',
                 'right-elbow',
                 'right-wrist',
                 'left-wheel',
                 'left-z',
                 'left-shoulder',
                 'left-elbow',
                 'left-wrist']

    for actuator in actuators:
        print(create_actuator(actuator))

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
