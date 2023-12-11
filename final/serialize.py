import os
import sys
sys.path.append(os.path.join (os.path.dirname(__file__), '/home/yue/Apps/flatbuffers/python'))
import flatbuffers    # this is the flatbuffers package we import
import time   # we need this get current time
import numpy as np  # to use in our vector field
import zmq   # we need this for additional constraints provided by the zmq serialization
from custom_msg import ChatMessageClass  # our response message in native format
import OgTeam1PA1.ChatMessageTable as msg   # this is the generated code by the flatc compiler

# This is the method we will invoke from our driver program
def serialize (cm):
    # first obtain the builder object   
    builder = flatbuffers.Builder (0)

    user = builder.CreateString (cm.user)  # create the contents string for the content field
    password = builder.CreateString (cm.password)  # create the contents string for the content field
    receiver = builder.CreateString (cm.receiver)  # create the contents string for the content field
    contents = builder.CreateString (cm.contents)  # create the contents string for the content field
    
    # let us create the serialized msg by adding contents to it.
    msg.Start (builder)  # serialization starts with the "Start" method
    msg.AddUser (builder, user)  # serialize contents   
    msg.AddPassword (builder, password)  # serialize contents   
    msg.AddReceiver (builder, receiver)  # serialize contents   
    msg.AddContents (builder, contents)  # serialize contents    
    serialized_msg = msg.End (builder)  # get the topic of all these fields
    
    # end the serialization process
    builder.Finish (serialized_msg)

    # get the serialized buffer
    buf = builder.Output ()

    # return this serialized buffer to the caller
    return buf

# serialize the custom message to iterable frame objects needed by zmq
def serialize_to_frames (cm):
  """ serialize into an interable format """
  return [serialize (cm)]
  
  
# deserialize the incoming serialized structure into native data type
def deserialize (buf):
        
    # Create an instance of ResponseMessageTable        
    cm = ChatMessageClass ()    
    packet = msg.ChatMessageTable.GetRootAs (buf, 0)
    cm.user = packet.User ()  # contents
    cm.password = packet.Password ()  # contents
    cm.receiver = packet.Receiver ()  # contents
    cm.contents = packet.Contents ()  # contents

    return cm
    
# deserialize from frames
def deserialize_from_frames (recvd_seq):
  """ This is invoked on list of frames by zmq """
  
  assert (len (recvd_seq) == 1)
  cm = deserialize (recvd_seq[0])  # hand it to our deserialize method

  # assuming only one frame in the received sequence, we just send this deserialized
  # custom message
  return cm
