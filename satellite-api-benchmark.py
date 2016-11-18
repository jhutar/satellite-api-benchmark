#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Utility supposed to provide CLI interface to satellite_api_benchmark
"""

import sys

import satellite_api_benchmark


def main():
    """Main"""
    # Load params
    procs = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    hostname = sys.argv[4]
    action = sys.argv[5]

    sab = satellite_api_benchmark.Satellite5(username, password, hostname)
    if action == 'setup':
        sab.check()
        sab.setup()
    elif action == 'run':
        results = sab.run()
        print results
    elif action == 'cleanup':
        orgs = [int(i) for i in sys.argv[6].split(',')]
        sab.cleanup(orgs)
    else:
        print "ERROR: Unknown action"
        sys.exit(1)

if __name__ == '__main__':
    main()
