from cvra_rpc.message import *
import logging

def foo(args):
    logging.info('Setting actuator position {}'.format(args))


TARGET = ('0.0.0.0', 20000)
callbacks = {'actuator_position': foo}

logging.getLogger().setLevel(logging.INFO)
RequestHandler = create_request_handler(callbacks)
server = socketserver.UDPServer(TARGET, RequestHandler)
server.serve_forever()
