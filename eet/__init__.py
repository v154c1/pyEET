import EET
from Trzba import *


if __name__ == '__main__':
    import sys
    import logging

    logging.basicConfig(level=logging.INFO)

    e = EET.EET(sys.argv[1], sys.argv[2], 1, 'stodola')
    p = e.create_payment('P12321', 3248, test=False)
    p.set_amount(TAX_BASIC, 1000, 210)
    r = e.send_payment(p)
    print(r)
    
