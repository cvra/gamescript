from HomingHandler import HomeZ

homez = HomeZ("192.168.3.20")
homez.add(['right-elbow'], 0.9, [0.5, 1.])
print(homez.start())
