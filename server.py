from cvra_rpc.service_call import *
import socketserver, logging

def create_actuator_cb(args):
    logging.info("Creating actuator {}".format(args))

if __name__ == "__main__":
    MyTCPHandler = create_request_handler({'actuator_create_driver':create_actuator_cb})

    HOST, PORT = "localhost", 20001
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    server.serve_forever()
