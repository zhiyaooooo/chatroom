# Define the classes based on schema

from typing import List
from dataclasses import dataclass
from enum import IntEnum

# response message
class ChatMessageClass:
  def __init__(self):
    self.user = ""
    self.password = ""
    self.receiver = ""
    self.contents = ""
  def __str__(self):
    return f"user: {self.user}\n" \
           f"password: {self.password}\n" \
           f"receiver: {self.receiver}\n" \
           f"contents: {self.contents}\n"


# test if we can instantiate an object of ThreeTypeMessage and assign values to it
def main():
  cm = ChatMessageClass ()
  cm.contents = "hello world"  
  print(cm)

# make sure test code won't be executed when imported to other files
if __name__ == '__main__':
  main ()
