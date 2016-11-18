#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Utility supposed to provide CLI interface to satellite_api_benchmark
"""

import sys
import multiprocessing

import tabulate

import satellite_api_benchmark


def print_results(results):
    """Print nicely formatted results of the measurements"""
    # Main table
    header = ['process', 'method', 'repeats', 'avg duration']
    summary = {}   # for summary data, assumes we do not call one method with different inputs
    total = 0   # for grand total duration
    table = []
    for i in range(len(results)):
        for r in results[i]:
            # Fill data for main table
            duration = float(r['end']-r['start'])
            result = [r['method'], r['repeats'], duration/r['repeats']]
            table.append([i]+result)
            # Fill data for summary table
            if r['method'] not in summary:
                summary[r['method']] = {'repeats': 0, 'duration': 0}
            summary[r['method']]['repeats'] += r['repeats']
            summary[r['method']]['duration'] += duration
            # Update total duration
            total += duration
    print tabulate.tabulate(table, headers=header, tablefmt="psql")
    # Summary table
    print
    summary_table = []
    summary_header = ['methods sumarised', 'avg duration']
    for method, data in summary.items():
        summary_table.append([method, data['duration']/data['repeats']])
    print tabulate.tabulate(summary_table, headers=summary_header, tablefmt="psql")
    # Total
    print
    print "TOTAL %s %s" % (len(results), total)


def setup(username, password, hostname):
    """Create all required elements"""
    sab = satellite_api_benchmark.Satellite5(username, password, hostname)
    sab.check()
    return sab.setup()


def run(username, password, hostname):
    """Run benchmark"""
    sab = satellite_api_benchmark.Satellite5(username, password, hostname)
    return sab.run()


def cleanup(username, password, hostname, orgs):
    """Cleanup all setup and temporary files we have created"""
    sab = satellite_api_benchmark.Satellite5(username, password, hostname)
    sab.cleanup(orgs)


def main():
    """Main"""
    # Load params
    username = sys.argv[1]
    password = sys.argv[2]
    hostname = sys.argv[3]
    action = sys.argv[4]

    # What are we going to do?
    if action == 'setup':
        out = setup(username, password, hostname)
        print "CREATED %s" % ','.join(out)
    elif action == 'run':
        try:
            procs = int(sys.argv[5])
        except IndexError:
            procs = 1
        # Run without multiprocessing module when number of procs is default
        # 1 as it makes it easier to see tracebacks
        if procs > 1:
            results = []
            # Define process pools and start processes
            pool = multiprocessing.Pool(processes=procs)
            for i in range(procs):
                results.append(
                    pool.apply_async(
                        run,
                        (username, password, hostname)
                    )
                )
            # Do not allow submitting more processes and wait for workers to exit
            pool.close()
            pool.join()
            # Get the results
            results_out = []
            for result in results:
                results_out.append(result.get())
            print_results(results_out)
        else:
            result = run(username, password, hostname)
            print_results([result])
    elif action == 'cleanup':
        orgs = [int(i) for i in sys.argv[5].split(',')]
        cleanup(username, password, hostname, orgs)
    else:
        print "ERROR: Unknown action"
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
