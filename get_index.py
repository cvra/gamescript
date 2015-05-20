from HomingHandler import Indexer

indexer = Indexer("192.168.3.20")
indexer.add(['right-shoulder', 'right-elbow', 'right-wrist'])
print(indexer.start())
