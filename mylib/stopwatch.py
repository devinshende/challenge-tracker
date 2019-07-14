# class I use later on to time things that take a long time
from time import time,sleep
from termcolor import cprint, colored
from random import *

class stopwatch():
  def __init__(self, msg=""):
    self.t0 = time()
    self.msg = msg
  
  def stop(self):
    self.elapsed = round(time() - self.t0,1)
    
    # the math is from stack overflow
    hours = self.elapsed // 3600 % 24
    minutes = self.elapsed // 60 % 60
    seconds = self.elapsed % 60
    
    hours = round(hours)
    minutes = round(minutes)
    seconds = round(seconds,1)
    
    if self.msg:
      m = "Elapsed Time For "+self.msg+": "
    else:
      m = "Elapsed Time: "
    if hours and minutes and seconds:
      msg = f"{m}{hours} hours, {minutes} minutes, and {seconds} seconds"
    elif minutes and seconds:
      if minutes == 1.0:
        msg = f"{m}1 minute and {seconds} seconds"
      else: msg = f"{m}{minutes} minutes and {seconds} seconds"
    elif seconds:
      msg = f"{m}{seconds} seconds"
    elif seconds == 0.0:
      msg = f"{m}{round(time()-self.t0,6)} seconds" # give time rounded to 6 places (not 1) if it is 0 when rounded. Ex: 0.000143 seconds
    else: 
      msg = "something went wrong with stopwatch class\n"+str(self.elapsed)+" seconds"
    cprint(msg,"red")