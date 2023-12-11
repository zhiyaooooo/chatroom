# import the needed packages
import os
import sys
sys.path.append(os.path.join (os.path.dirname(__file__), '/home/yue/Apps/flatbuffers/python'))
import flatbuffers    # this is the flatbuffers package we import
import time  # needed for timing measurements and sleep
import random  # random number generator
import argparse  # argument parser
import zmq   # for ZeroMQ
from threading import Thread

from custom_msg import ChatMessageClass  # our custom message in native format
import serialize  # this is from the file serialize.py in the same directory
##################################
# Driver program
##################################


def driver (args):
  try:
    contextREP = zmq.Context ()   # returns a singleton object
    contextPUB = zmq.Context ()   # returns a singleton object
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining context: {}".format (err))
    return
  except:
    print ("Some exception occurred getting context {}".format (sys.exc_info()[0]))
    return

  try:
    socketREP = contextREP.socket (zmq.REP)
    socketPUB = contextPUB.socket (zmq.PUB)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error obtaining REP socket: {}".format (err))
    return
  except:
    print ("Some exception occurred getting REP socket {}".format (sys.exc_info()[0]))
    return

  try:
    bind_stringREP = "tcp://" + args.intf + ":" + str (args.portREP)
    bind_stringPUB = "tcp://" + args.intf + ":" + str (args.portPUB)
    socketREP.bind (bind_stringREP)
    socketPUB.bind (bind_stringPUB)
  except zmq.ZMQError as err:
    print ("ZeroMQ Error binding REP socket: {}".format (err))
    socketREP.close ()
    return
  except:
    print ("Some exception occurred binding REP socket {}".format (sys.exc_info()[0]))
    socketREP.close ()
    return

  # Use the ZMQ's recv_serialized method to send the custom message
  def recv_request ():
    """ receive serialized request"""
    try:
      cm = socketREP.recv_serialized (serialize.deserialize_from_frames, copy=True)
      return cm
    except zmq.ZMQError as err:
      print ("ZeroMQ Error receiving serialized message: {}".format (err))
      raise
    except:
      print ("Some exception occurred with recv_serialized {}".format (sys.exc_info()[0]))
      raise
      
  # Use the ZMQ's send_serialized method to send the custom message
  def send_reply (cm):
    """ Send serialized reply"""
    try:
      socketREP.send_serialized (cm, serialize.serialize_to_frames)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error serializing reply: {}".format (err))
      raise
    except:
      print ("Some exception occurred with send_serialized {}".format (sys.exc_info()[0]))
      raise
    
  def send_pub (cm):
    """ Send serialized reply"""
    try:
      socketPUB.send_serialized (cm, serialize.serialize_to_frames)
    except zmq.ZMQError as err:
      print ("ZeroMQ Error serializing reply: {}".format (err))
      raise
    except:
      print ("Some exception occurred with send_serialized {}".format (sys.exc_info()[0]))
      raise


  # since we are a server, we service incoming clients forever
  while True:
    receiveMsg = recv_request ()    
    print (receiveMsg)    
    print("\n")
    
    cm = ChatMessageClass()
    cm.contents = receiveMsg.contents
    
    # send serialized reply to client.
    print(cm)
    send_pub (cm)
    send_reply (ChatMessageClass())

    #  Do some 'work'. In this case we just sleep.
    time.sleep (0.05)



##################################
# Command line parsing
##################################
def parseCmdLineArgs ():
  # parse the command line
  parser = argparse.ArgumentParser ()

  # add optional arguments
  parser.add_argument ("-i", "--intf", default="*", help="Interface to bind to (default: *)")
  parser.add_argument ("-pREP", "--portREP", type=int, default=5555, help="REP Port to bind to (default: 5555)")
  parser.add_argument ("-pPUB", "--portPUB", type=int, default=6666, help="PUB Port to bind to (default: 6666)")
  args = parser.parse_args ()

  return args
    
#------------------------------------------
# main function
def main ():
  # first parse the command line args
  parsed_args = parseCmdLineArgs ()
    
  # start the driver code
  driver (parsed_args)

#----------------------------------------------
if __name__ == '__main__':
  main ()
