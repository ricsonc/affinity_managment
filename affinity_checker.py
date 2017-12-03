#!/usr/bin/env python

import random
import time
import psutil
import pwd
import os

USERNAME = pwd.getpwuid(os.getuid()).pw_name

CHECKER = 'CHECKER'
NONCHECKER = 'NONCHECKER'
OTHERUSER = 'OTHERUSER'

EXEMPT = ['sshd']

def print_process(process):
    print '===='
    print 'PID:', process.pid
    print 'USER:', process.username()
    print 'CMDLINE:', process.cmdline()
    print 'TYPE:', get_type(process)
    print 'AFFINITY:', process.cpu_affinity()

def get_type(process):
    if process.username() != USERNAME:
        return OTHERUSER

    cmd = process.cmdline()
    if cmd and (('sshd' in cmd[0]) or ('/bin/bash' in cmd[0])):
        return OTHERUSER #technically not, but we want to avoid

    if (len(cmd) == 2) and ('affinity_checker' in cmd[1]) and ('python' in cmd[0]):
        return CHECKER
    
    return NONCHECKER

def get_checkers():
    checkers = []
    non_checkers = []
    for process in psutil.process_iter():
        type_ = get_type(process)
        if type_ == CHECKER:
            checkers.append(process)
        elif type_ == NONCHECKER:
            non_checkers.append(process)
        elif type_ == OTHERUSER:
            pass
    return checkers, non_checkers

def affinity_of_checkers(checkers):
    total_affinity = []
    for checker in checkers:
        affinity = checker.cpu_affinity()
        total_affinity.extend(affinity)
    return list(set(total_affinity))

def me():
    return psutil.Process(os.getpid())

def mainloop():
    period = 30
    c = 0
    while 1:
        print 'cycle', c
        checkers, non_checkers = get_checkers()
        print '%d checkers found, %d non_checkers found' % (len(checkers), len(non_checkers))
        affinity = affinity_of_checkers(checkers)
        print 'affinity should be', affinity

        setcount = 0
        for process in non_checkers:
            try:
                cpu_affinity = process.cpu_affinity()
            except psutil.NoSuchProcess:
                print 'process does not exist'
                continue

            if not frozenset(cpu_affinity).issubset(frozenset(affinity)):
                try:
                    process.cpu_affinity(affinity) #set
                    #process.cpu_affinity([random.choice(affinity)])
                    setcount += 1                    
                except psutil.AccessDenied:
                    print 'warning: access denied for one process'

        print 'set affinity for %d processes' % setcount
        c += 1
        time.sleep(period)
        
if __name__ == '__main__':
    #me().cpu_affinity([0,1])
    mainloop()
