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

    # Run
    sab = satellite_api_benchmark.Satellite5(username, password, hostname)
    sab.check()
    sab.setup()
    results = sab.run()
    sab.cleanup()

    # Report
    print results

if __name__ == '__main__':
    main()
