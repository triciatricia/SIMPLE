import os
import time
import sys

p=os.path.join(os.environ['EMANDIR'],"lib")

sys.path.append(p)
sys.path.append("/usr/lib/python2.3/site-packages/")
os.environ['PYTHONPATH'] = p
