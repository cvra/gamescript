from cvra_rpc.service_call import *
import socket
import msgpack

HOST, PORT = "localhost", 20002

result = call((HOST, PORT), 'button_released', ['start'])
print(result)
