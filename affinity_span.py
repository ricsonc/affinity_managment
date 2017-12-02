#!/usr/bin/env python

import time
import psutil
import pwd
import os
from collections import defaultdict

with open('users.cache') as f:
    USERS = map(lambda x: x.strip(), f.readlines())

def get_spans():
    spans = defaultdict(list)
    for process in psutil.process_iter():
        spans[process.username()].extend(process.cpu_affinity())
    spans = [(k, list(set(v))) for (k,v) in spans.items()]
    return sorted(spans, key = lambda x: len(x[1]))[::-1]

def print_spans():
    for user, span in get_spans():
        if user in USERS:
            print 'USER %s is using %d processors' % (user, len(span))
            print span

if __name__ == '__main__':
    period = 10
    while 1:
        print '='*10
        print_spans()
        time.sleep(period)
