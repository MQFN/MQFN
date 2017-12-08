import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
from bbmq.consumer.consumer import Consumer

cons = Consumer("PR_PAYLOADS")
cons.connect()
while True:
    print "-1 to stop, anything else to fetch"

    a = raw_input()

    if a == "-1":
        cons.close_socket()
        break
    else:
        print "message now:"
        print cons.fetch()



