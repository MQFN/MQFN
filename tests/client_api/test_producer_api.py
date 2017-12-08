import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
from bbmq.producer import Producer

prod = Producer("PR_PAYLOADS")
prod.connect()
while True:
    print "message now, -1 to stop"

    a = raw_input()

    if a == -1:
        prod.close_socket()
        break
    else:
        prod.publish(a)



