from HomingHandler import HomingHandler

hominghandler = HomingHandler("192.168.3.20")
hominghandler.add(['right-shoulder', 'right-elbow', 'right-wrist'])
print(hominghandler.start())
