Satellite API benchmark
=======================

This tool runs certain (supposedly stable) set of API calls against Red Hat Satellite 5 (or Spacewalk) server. Its goal is to provide single numbed related to API performance (and breakdown for individual groups of calls).

Installation (RHEL6)
--------------------

Make i work on RHEL 6::

    rpm -ivh https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm
    yum -y install python-virtualenv git rpm-build screen   # screen is completely optional but useful
    git clone https://github.com/jhutar/satellite-api-benchmark.git
    cd satellite-api-benchmark
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    wget  --quiet  --output-document=rpmfluff.py 'https://pagure.io/rpmfluff/raw/956609fdb7ffe539128f13dba80480728ea913fe/f/rpmfluff.py'
    export PYTHONPATH=/usr/lib64/python2.6/site-packages/

Running
-------

Before running the tool, make sure your server have empty database (no channels, no users, no systems...).

To run API call workload against `hostname` server (localhost strongly suggested so networking performance does not play role in the result) with admin user `admin` (whose password is `password`), and to run the workload `5` times in parallel (maybe you are interested how the performance degrades based on number of concurrent runs? When not provided, `1` is default.)::

    ./satellite-api-benchmark.py admin password hostname check
    ./satellite-api-benchmark.py admin password hostname setup
    ./satellite-api-benchmark.py admin password hostname run 5   # actual test
    ./satellite-api-benchmark.py admin password hostname cleanup
    ./satellite-api-benchmark.py admin password hostname check
