# import the needed packages
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '/home/yue/Apps/flatbuffers/python'))
import flatbuffers  # this is the flatbuffers package we import
import time  # needed for timing measurements and sleep
import argparse  # argument parser
import zmq  # for ZeroMQ
from threading import Thread

from custom_msg import ChatMessageClass  # our custom message in native format
import serialize  # this is from the file serialize.py in the same directory
import os
import sys
import tkinter as tk
from threading import Thread
import zmq
import flatbuffers
from custom_msg import ChatMessageClass
import serialize


##################################
# Driver program
##################################


# class about creating a socket and using a socket to send/receive messages
class REQREP:
    def __init__(self, addr, port, name):
        self.addr = addr  # IP address
        self.port = port  # port number
        self.name = name  # name of connection
        self.socket = None

    # create a REQ socket and connect with server
    def configure(self):
        context = zmq.Context()  # returns a singleton object
        self.socket = context.socket(zmq.REQ)
        # connect
        connect_string = "tcp://" + self.addr + ":" + str(self.port)
        self.socket.connect(connect_string)

        # Use the ZMQ's send_serialized method to send message

    def send_request(self, cm):
        self.socket.send_serialized(cm, serialize.serialize_to_frames)

    # Use the ZMQ's recv_serialized method to receive response message
    def recv_reply(self):
        cm = self.socket.recv_serialized(serialize.deserialize_from_frames, copy=True)
        return cm


class SUBPUB:
    def __init__(self, addr, port, name):
        self.addr = addr  # IP address
        self.port = port  # port number
        self.name = name  # name of connection
        self.socket = None

    # create a REQ socket and connect with server
    def configure(self):
        context = zmq.Context()  # returns a singleton object
        self.socket = context.socket(zmq.SUB)

        try:
            context = zmq.Context()  # returns a singleton object
        except zmq.ZMQError as err:
            print("ZeroMQ Error obtaining context: {}".format(err))
            return
        except:
            print("Some exception occurred getting context {}".format(sys.exc_info()[0]))
            return

        try:
            self.socket = context.socket(zmq.SUB)
        except zmq.ZMQError as err:
            print("ZeroMQ Error obtaining REQ socket: {}".format(err))
            return
        except:
            print("Some exception occurred getting REQ socket {}".format(sys.exc_info()[0]))
            return

        try:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        except zmq.ZMQError as err:
            print("ZeroMQ Error setting prefix: {}".format(err))
            return
        except:
            print("Some exception occurred setting prefix {}".format(sys.exc_info()[0]))
            return

        try:
            # connect
            connect_string = "tcp://" + self.addr + ":" + str(self.port)
            self.socket.connect(connect_string)
        except zmq.ZMQError as err:
            print("ZeroMQ Error connecting REQ socket: {}".format(err))
            self.socket.close()
            return
        except:
            print("Some exception occurred connecting REQ socket {}".format(sys.exc_info()[0]))
            self.socket.close()
            return

    # Use the ZMQ's recv_serialized method to receive response message
    def recv_pub(self):
        """ receive deserialized reply"""
        try:
            # receive deserialized message
            cm = self.socket.recv_serialized(serialize.deserialize_from_frames, copy=True)
            return cm
        except zmq.ZMQError as err:
            print("ZeroMQ Error receiving serialized message: {}".format(err))
            raise
        except:
            print("Some exception occurred with recv_serialized {}".format(sys.exc_info()[0]))
            raise


##################################
# Driver program
##################################
def driver(args):
    # create sockets for two servers and configure them
    REQREPObject = REQREP(args.addr, args.portREQ, args.nameREQ)
    REQREPObject.configure()
    SUBPUBObject = SUBPUB(args.addr, args.portSUB, args.nameSUB)
    SUBPUBObject.configure()

    # ClientToHealth.configure ()
    # a method to send one message and receive one response message
    def sendAndReceiveFunction():
        while True:
            # now send the serialized custom message for the number of desired iterations
            cm = ChatMessageClass()
            cm.contents = input("")
            # send serialized message to server and receive deserialized message.
            REQREPObject.send_request(cm)

            cm = REQREPObject.recv_reply()
            cm.contents = str(cm.contents)[2:-1]  # raw format is b'thisiscontent', delete b'' from the original string
            print(cm)

    def receivePubFunction():
        while True:
            cm = SUBPUBObject.recv_pub()
            cm.contents = str(cm.contents)[2:-1]  # raw format is b'thisiscontent', delete b'' from the original string
            print(cm.contents)

    receivePubThread = (Thread(target=receivePubFunction, args=( )))
    receivePubThread.start()

    sendThread = (Thread(target=sendAndReceiveFunction, args=( )))
    sendThread.start()


##################################
# Command line parsing
##################################
def parseCmdLineArgs():
    # parse the command line
    parser = argparse.ArgumentParser()

    # add optional arguments
    parser.add_argument("-a", "--addr", default="127.0.0.1",
                        help="IP Address to connect to (default: localhost i.e., 127.0.0.1)")
    parser.add_argument("-pREQ", "--portREQ", type=int, default=5555,
                        help="Port that server is listening on (default: 5555)")
    parser.add_argument("-nREQ", "--nameREQ", default="REQ-REP socket", help="Name to include in each message")
    parser.add_argument("-pSUB", "--portSUB", type=int, default=6666,
                        help="Port that server is listening on (default: 5555)")
    parser.add_argument("-nSUB", "--nameSUB", default="SUB-PUB socket", help="Name to include in each message")
    args = parser.parse_args()

    return args


class ChatApp:
  def __init__(self, root, REQREPObject, SUBPUBObject, username):
    self.root = root
    self.REQREPObject = REQREPObject
    self.SUBPUBObject = SUBPUBObject
    self.username = username
    # Setting up the GUI
    self.setup_gui()

    # Start the thread for receiving messages
    self.start_receiving()

  def setup_gui(self):
    self.root.title("Chat Room")
    self.root.geometry("500x400")

    # Text box for displaying messages
    self.chat_content = tk.Text(self.root, state='disabled')
    self.chat_content.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Entry box for typing messages
    self.message_entry = tk.Entry(self.root)
    self.message_entry.pack(padx=10, pady=10, fill=tk.X, expand=False)
    self.message_entry.bind("<Return>", self.send_message)

  def send_message(self, event=None):
    message = self.message_entry.get()
    if message:
      cm = ChatMessageClass()
      cm.user = self.username
      cm.contents = cm.user + ": " + message

      try:
        self.REQREPObject.send_request(cm)
        # Wait for a reply here before enabling the next send, if using REQ/REP
        reply = self.REQREPObject.recv_reply()
        # Process reply if necessary
      except zmq.ZMQError as e:
        print("Error sending message:", e)
        # Handle the error appropriately
      finally:
        self.message_entry.delete(0, tk.END)

  def receive_message(self):
    while True:
      cm = self.SUBPUBObject.recv_pub()
      message = str(cm.contents)[2:-1]  # processing the message
      self.update_chat_content(message)

  def start_receiving(self):
    receive_thread = Thread(target=self.receive_message)
    receive_thread.daemon = True  # Daemonize thread
    receive_thread.start()

  def update_chat_content(self, message):
    self.chat_content.configure(state='normal')
    self.chat_content.insert(tk.END, message + '\n')
    self.chat_content.configure(state='disabled')
    self.chat_content.see(tk.END)  # Scroll to the bottom

# ------------------------------------------
# main function
def main():
    parsed_args = parseCmdLineArgs()

    # New window to ask for username
    login_root = tk.Tk()
    login_root.title("Enter Username")
    tk.Label(login_root, text="Username:").pack(side="left")
    username_entry = tk.Entry(login_root)
    username_entry.pack(side="left")

    def on_login_click():
        username = username_entry.get()
        if username:
            login_root.destroy()  # Close the login window
            chat_room(parsed_args, username)  # Initialize the chat room with the username
        else:
            tk.messagebox.showerror("Error", "Username cannot be empty!")

    tk.Button(login_root, text="Enter Chat", command=on_login_click).pack()
    login_root.mainloop()

def chat_room(parsed_args, username):
    root = tk.Tk()
    REQREPObject = REQREP(parsed_args.addr, parsed_args.portREQ, parsed_args.nameREQ)
    REQREPObject.configure()
    SUBPUBObject = SUBPUB(parsed_args.addr, parsed_args.portSUB, parsed_args.nameSUB)
    SUBPUBObject.configure()

    app = ChatApp(root, REQREPObject, SUBPUBObject, username)
    root.mainloop()

# ----------------------------------------------
if __name__ == '__main__':
    main()