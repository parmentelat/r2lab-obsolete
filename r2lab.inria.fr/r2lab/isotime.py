import time

wire_timeformat = "%Y-%m-%dT%H:%M:%SZ"

def is_future(iso_string):
    the_time = time.strptime(iso_string, wire_timeformat)
    now = time.gmtime(time.time())
#    print("now", now, "the_time", the_time)
    return now <= the_time

def expiration_date(delay):
    now = time.time()
    new_expire = time.gmtime(now + delay)
    return time.strftime(wire_timeformat, new_expire)


############################## test
if __name__ == '__main__':
    for delay in range(-9000, 10000, 2000) + [ -10, 10] :
        ref = expiration_date(delay)
        print("delay from now = {} - ref={}, is_future={}"
              .format(delay, ref, is_future(ref)))
