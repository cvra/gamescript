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

def move_base(distance):
    setpoints:
        right-wheel += distance / (2 * pi * right-wheel-radius)
        left-wheel += distance / (2 * pi * left-wheel-radius)

def turn_base(angle):
    setpoints:
        right-wheel += angle * wheelbase / (2 * pi * right-wheel-radius)
        left-wheel += - angle * wheelbase / (2 * pi * left-wheel-radius)

def move_arm(flip, z, shoulder, elbow, wrist):
    setpoints:
        flip-z = z
        flip-shoulder = shoulder
        flip-elbow = elbow
        flip-wrist = wrist
