#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""This module is supposed to provide functions to test Red Hat Satellite 5
   API performance."""

import sys
import xmlrpclib
if sys.version_info >= (2, 7, 9):
    import ssl


class Satellite5(object):
    """This class is supposed to provide functions to test Red Hat Satellite 5
       API performance."""

    def __init__(self, username, password, hostname):
        self.client = None
        self.key = None
        self.username = username
        self.password = password
        self.hostname = hostname
        self._login()

    def check(self):
        """Check that the Satellite is empty"""
        pass

    def setup(self):
        """Create all the required setup to run the workload"""
        pass

    def cleanup(self):
        """Cleanup all the setup we did in setup()"""
        pass

    def run(self):
        """Run the API benchmark"""
        pass

    def _login(self):
        """Populate self.key"""
        server_url = "https://%s/rpc/api" % self.hostname
        if sys.version_info >= (2, 7, 9):
            # Workaround ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
            # certificate verify failed (_ssl.c:590) when we do not care
            # about security
            # pylint: disable=W0212
            context = ssl._create_unverified_context()
            self.client = xmlrpclib.Server(server_url, verbose=0,
                                           context=context)
        else:
            self.client = xmlrpclib.Server(server_url, verbose=0)
        self.key = self.client.auth.login(self.username, self.password)
