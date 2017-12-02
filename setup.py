#!/usr/bin/env python

import os

if 'matrix' not in os.uname()[1]:
    print 'please run me on the matrix root node! exiting without doing anything.'
    exit()

users = os.listdir('/home')

with open('users.cache', 'w') as f:
    for user in users:
        f.write(user+'\n')

    
