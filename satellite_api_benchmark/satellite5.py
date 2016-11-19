#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""This class is supposed to provide functions to test Red Hat Satellite 5
   API performance."""

import sys
import os
import time
import subprocess
import re
import shutil
import logging

import xmlrpclib
if sys.version_info >= (2, 7, 9):
    import ssl

import rpmfluff


logger = logging.getLogger(__name__)

def xmlrpc_login(server_url):
    """Generic login code"""
    if sys.version_info >= (2, 7, 9):
        # Workaround ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
        # certificate verify failed (_ssl.c:590) when we do not care
        # about security
        # pylint: disable=W0212
        context = ssl._create_unverified_context()
        return xmlrpclib.Server(server_url, verbose=0,
                                context=context)
    else:
        return xmlrpclib.Server(server_url, verbose=0)


class Satellite5(object):
    """This class is supposed to provide functions to test Red Hat Satellite 5
       API performance."""

    repeats_default = 10
    org_admin = 'benchmark-org-0-admin'
    org_pass = 'benchmark-org-0-pass'
    org_channel = 'benchmark-org-0-channel-0'
    hwinfo = [
        {'bus': 'pci', 'driver': 'agpgart-intel', 'pciType': '1',
         'prop4': '2193', 'prop1': '8086', 'prop2': '0044', 'prop3': '17AA',
         'detached': '0', 'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor DRAM Controller'},
        {'bus': 'pci', 'driver': 'i915', 'pciType': '1', 'prop4': '215A',
         'prop1': '8086', 'prop2': '0046', 'prop3': '17AA', 'detached': '0',
         'class': 'VIDEO',
         'desc': 'Intel Corporation|Core Processor Integrated Graphics Controller'},
        {'bus': 'pci', 'driver': 'mei', 'pciType': '1', 'prop4': '215F',
         'prop1': '8086', 'prop2': '3B64', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset HECI Controller'},
        {'bus': 'pci', 'driver': 'serial', 'pciType': '1', 'prop4': '2162',
         'prop1': '8086', 'prop2': '3B67', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset KT Controller'},
        {'bus': 'pci', 'driver': 'e1000e', 'pciType': '1', 'prop4': '2153',
         'prop1': '8086', 'prop2': '10EA', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|82577LM Gigabit Network Connection'},
        {'bus': 'pci', 'driver': 'ehci-pci', 'pciType': '1', 'prop4': '2163',
         'prop1': '8086', 'prop2': '3B3C', 'prop3': '17AA', 'detached': '0',
         'class': 'USB',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset USB2 Enhanced Host Controller'},
        {'bus': 'pci', 'driver': 'snd_hda_intel', 'pciType': '1',
         'prop4': '215E', 'prop1': '8086', 'prop2': '3B56', 'prop3': '17AA',
         'detached': '0', 'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset High Definition Audio'},
        {'bus': 'pci', 'driver': 'pcieport', 'pciType': '1', 'prop4': '2164',
         'prop1': '8086', 'prop2': '3B42', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset PCI Express Root Port 1'},
        {'bus': 'pci', 'driver': 'pcieport', 'pciType': '1', 'prop4': '2164',
         'prop1': '8086', 'prop2': '3B44', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset PCI Express Root Port 2'},
        {'bus': 'pci', 'driver': 'iwlwifi', 'pciType': '1', 'prop4': '1111',
         'prop1': '8086', 'prop2': '4238', 'prop3': '8086', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Centrino Ultimate-N 6300'},
        {'bus': 'pci', 'driver': 'pcieport', 'pciType': '1', 'prop4': '2164',
         'prop1': '8086', 'prop2': '3B48', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset PCI Express Root Port 4'},
        {'bus': 'pci', 'driver': 'pcieport', 'pciType': '1', 'prop4': '2164',
         'prop1': '8086', 'prop2': '3B4A', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset PCI Express Root Port 5'},
        {'bus': 'pci', 'driver': 'sdhci-pci', 'pciType': '1', 'prop4': '2133',
         'prop1': '1180', 'prop2': 'E822', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Ricoh Co Ltd|MMC/SD Host Controller'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2134',
         'prop1': '1180', 'prop2': 'E230', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Ricoh Co Ltd|R5U2xx (R5U230 / R5U231 / R5U241) [Memory Stick Host Controller]'},
        {'bus': 'pci', 'driver': 'firewire_ohci', 'pciType': '1', 'prop4': '2136',
         'prop1': '1180', 'prop2': 'E832', 'prop3': '17AA', 'detached': '0',
         'class': 'FIREWIRE',
         'desc': 'Ricoh Co Ltd|R5C832 PCIe IEEE 1394 Controller'},
        {'bus': 'pci', 'driver': 'ehci-pci', 'pciType': '1', 'prop4': '2163',
         'prop1': '8086', 'prop2': '3B34', 'prop3': '17AA', 'detached': '0',
         'class': 'USB',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset USB2 Enhanced Host Controller'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2165',
         'prop1': '8086', 'prop2': '2448', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|82801 Mobile PCI Bridge'},
        {'bus': 'pci', 'driver': 'lpc_ich', 'pciType': '1', 'prop4': '2166',
         'prop1': '8086', 'prop2': '3B07', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Mobile 5 Series Chipset LPC Interface Controller'},
        {'bus': 'pci', 'driver': 'ahci', 'pciType': '1', 'prop4': '2168',
         'prop1': '8086', 'prop2': '3B2F', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset 6 port SATA AHCI Controller'},
        {'bus': 'pci', 'driver': 'i801_smbus', 'pciType': '1', 'prop4': '2167',
         'prop1': '8086', 'prop2': '3B30', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset SMBus Controller'},
        {'bus': 'pci', 'driver': 'intel ips', 'pciType': '1', 'prop4': '2190',
         'prop1': '8086', 'prop2': '3B32', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|5 Series/3400 Series Chipset Thermal Subsystem'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2196',
         'prop1': '8086', 'prop2': '2C62', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor QuickPath Architecture Generic Non-core Registers'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2196',
         'prop1': '8086', 'prop2': '2D01', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor QuickPath Architecture System Address Decoder'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2196',
         'prop1': '8086', 'prop2': '2D10', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor QPI Link 0'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2196',
         'prop1': '8086', 'prop2': '2D11', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor QPI Physical 0'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2196',
         'prop1': '8086', 'prop2': '2D12', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor Reserved'},
        {'bus': 'pci', 'driver': 'unknown', 'pciType': '1', 'prop4': '2196',
         'prop1': '8086', 'prop2': '2D13', 'prop3': '17AA', 'detached': '0',
         'class': 'OTHER',
         'desc': 'Intel Corporation|Core Processor Reserved'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '1d6b',
         'prop2': '0002', 'detached': '0', 'class': 'OTHER',
         'desc': 'Linux Foundation|2.0 root hub'},
        {'bus': 'usb', 'driver': 'hub', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Hub Interface'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '8087',
         'prop2': '0020', 'detached': '0', 'class': 'OTHER',
         'desc': 'Intel Corp.|Integrated Rate Matching Hub'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '04fe',
         'prop2': '0008', 'detached': '0', 'class': 'OTHER',
         'desc': 'PFU, Ltd|None'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '04fe',
         'prop2': '0006', 'detached': '0', 'class': 'KEYBOARD',
         'desc': 'PFU, Ltd|None'},
        {'bus': 'usb', 'driver': 'usbhid', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB HID Interface'},
        {'bus': 'usb', 'driver': 'hub', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Hub Interface'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '0a5c',
         'prop2': '217f', 'detached': '0', 'class': 'OTHER',
         'desc': 'Broadcom Corp.|Bluetooth Controller'},
        {'bus': 'usb', 'driver': 'btusb', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Interface'},
        {'bus': 'usb', 'driver': 'btusb', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Interface'},
        {'bus': 'usb', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Interface'},
        {'bus': 'usb', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Interface'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '17ef',
         'prop2': '100a', 'detached': '0', 'class': 'OTHER',
         'desc': 'Lenovo|ThinkPad Mini Dock Plus Series 3'},
        {'bus': 'usb', 'driver': 'hub', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Hub Interface'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '17ef',
         'prop2': '480f', 'detached': '0', 'class': 'OTHER',
         'desc': 'Lenovo|Integrated Webcam [R5U877]'},
        {'bus': 'usb', 'driver': 'uvcvideo', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Interface'},
        {'bus': 'usb', 'driver': 'uvcvideo', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Interface'},
        {'bus': 'usb', 'driver': 'hub', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Hub Interface'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '1d6b',
         'prop2': '0002', 'detached': '0', 'class': 'OTHER',
         'desc': 'Linux Foundation|2.0 root hub'},
        {'bus': 'usb', 'driver': 'hub', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Hub Interface'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '8087',
         'prop2': '0020', 'detached': '0', 'class': 'OTHER',
         'desc': 'Intel Corp.|Integrated Rate Matching Hub'},
        {'bus': 'usb', 'driver': 'usb', 'pciType': '-1', 'prop1': '046d',
         'prop2': 'c52f', 'detached': '0', 'class': 'OTHER',
         'desc': 'Logitech, Inc.|Wireless Mouse M305'},
        {'bus': 'usb', 'driver': 'usbhid', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB HID Interface'},
        {'bus': 'usb', 'driver': 'usbhid', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB HID Interface'},
        {'bus': 'usb', 'driver': 'hub', 'pciType': '-1', 'detached': '0',
         'class': 'OTHER', 'desc': 'USB Hub Interface'},
        {'bus': 'ata', 'driver': 'unknown', 'pciType': '-1', 'device': 'sda',
         'detached': '0', 'class': 'HD', 'desc': 'HITACHI_HTS725050A9A364'},
        {'bus': 'ata', 'driver': 'unknown', 'pciType': '-1', 'device': 'sr0',
         'detached': '0', 'class': 'CDROM', 'desc': 'MATSHITADVD-RAM_UJ890'},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'sd', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'sr', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'bus': 'scsi', 'driver': 'unknown', 'pciType': '-1', 'detached': '0',
         'class': 'SCSI', 'desc': ''},
        {'count': 4, 'model_ver': '37', 'speed': 1198, 'cache': '4096 KB',
         'model_number': '6', 'bogomips': '5320.05', 'platform': 'x86_64',
         'other': 'fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 cx16 xtpr pdcm sse4_1 sse4_2 popcnt aes lahf_lm ida arat dtherm tpr_shadow vnmi flexpriority ept vpid',
         'model_rev': '2',
         'model': 'Intel(R) Core(TM) i7 CPU       M 620  @ 2.67GHz',
         'type': 'GenuineIntel', 'class': 'CPU', 'desc': 'Processor'},
        {'ram': '3753', 'class': 'MEMORY', 'swap': '5823'},
        {'ip6addr': '::1', 'hostname': 'system.example.com',
         'ipaddr': '10.13.129.83', 'class': 'NETINFO'},
        {'product': '4313CTO', 'vendor': 'LENOVO', 'bios_vendor': 'LENOVO',
         'system': '4313CTO ThinkPad T510', 'bios_release': '12/22/2009',
         'board': 'LENOVO', 'bios_version': '6MET42WW (1.05 )',
         'class': 'DMI',
         'asset': '(chassis: R8348CE) (chassis: No Asset Information) (board: 1ZHP001Z2F3) (system: R8348CE)'},
        {'class': 'NETINTERFACES',
         'lo': {'ipaddr': '127.0.0.1', 'module': 'loopback',
                'broadcast': '0.0.0.0', 'netmask': '255.0.0.0',
                'ipv6': [{'scope': 'host', 'netmask': 128, 'addr': '::1'}],
                'hwaddr': '00:00:00:00:00:00'},
         'wlan0': {'ipaddr': '10.192.54.148', 'module': 'iwlwifi',
                   'broadcast': '10.192.55.255', 'netmask': '255.255.252.0',
                   'ipv6': [{'scope': 'link', 'netmask': 64, 'addr': 'fe80::224:d7ff:fe07:a18c'}],
                   'hwaddr': '00:24:d7:07:a1:8c'},
         'virbr0': {'ipaddr': '192.168.122.1', 'module': 'bridge',
                    'broadcast': '192.168.122.255', 'netmask': '255.255.255.0',
                    'ipv6': [], 'hwaddr': '52:54:00:ce:eb:21'},
         'virbr0-nic': {'ipaddr': '', 'module': 'tun', 'broadcast': '',
                        'netmask': '', 'ipv6': [],
                        'hwaddr': '52:54:00:ce:eb:21'},
         'eth0': {'ipaddr': '10.13.129.83', 'module': 'e1000e',
                  'broadcast': '10.13.129.255', 'netmask': '255.255.254.0',
                  'ipv6': [{'scope': 'link', 'netmask': 64, 'addr': 'fe80::226:2dff:fef1:390a'}],
                  'hwaddr': '00:26:2d:f1:39:0a'}}]

    def __init__(self, username, password, hostname):
        self.client = None
        self.key = None
        self.username = username
        self.password = password
        self.hostname = hostname
        self.actions = []
        self.created = []
        self._login()

    def check(self):
        """Check that the Satellite is empty"""
        assert len(self.client.org.listOrgs(self.key)) == 1, "There should be exactly one organization"
        ent = None
        for ent in self.client.org.listSystemEntitlements(self.key):
            if ent['label'] == 'enterprise_entitled':
                break
        assert ent is not None
        assert ent['label'] == 'enterprise_entitled', "Checking %s" % ent
        assert ent['used'] == 0, "Checking %s" % ent
        assert ent['allocated'] == 0, "Checking %s" % ent
        assert ent['free'] >= 100, "Checking %s" % ent
        assert ent['unallocated'] >= 0, "Checking %s" % ent
        assert len(self.client.channel.listAllChannels(self.key)) == 0, "There should be no channels"
        assert len(self.client.org.listUsers) == 1
        assert len(self.client.system.listSystems(self.key)) == 0, "There should be no systems"

    def setup(self):
        """Create all the required setup to run the workload"""
        logger.info("Building packages")
        for i in range(500):
            p = rpmfluff.SimpleRpmBuild('benchmark-org-0-package-%s' % i, '0.1', '1')
            p.add_installed_directory('/usr/share/benchmark-org-0-package-%s' % i, mode=755)
            p.add_installed_file('/usr/share/benchmark-org-0-package-%s/something.txt' % i, rpmfluff.SourceFile('something.txt', "This is a test\n"), mode='0644')
            p.add_description('This rpm is a very simple one. Just food for a channel.')
            p.make()
            p = rpmfluff.SimpleRpmBuild('benchmark-org-0-package-%s' % i, '0.2', '1')
            p.add_installed_directory('/usr/share/benchmark-org-0-package-%s' % i, mode=755)
            p.add_installed_file('/usr/share/benchmark-org-0-package-%s/something.txt' % i, rpmfluff.SourceFile('something.txt', "This is a new test\n"), mode='0644')
            p.add_description('This rpm is a very updated one.')
            p.make()

        logger.info("Creating orgs")
        for i in range(100):
            # Create org
            params = [
                'benchmark-org-%s' % i,   # orgName
                'benchmark-org-%s-admin' % i,   # adminLogin
                'benchmark-org-%s-pass' % i,   # adminPassword
                'Mr.',   # prefix
                'Mark',   # firstName
                'Bench',   # lastName
                'root@localhost',   # email
                False   # usePamAuth
            ]
            org = self._api('org.create', *params)
            # In first org we need lots of system entitments, no need for channel
            # entitlements as we will use custom channel
            org_system_entitlements = 1
            if i == 0:
                org_system_entitlements = 1000
            # Add system entitlements
            s_entitlements = ['enterprise_entitled', 'provisioning_entitled']
            for se in s_entitlements:
                params = [
                    org['id'],   # orgId
                    se,   # label
                    org_system_entitlements   # allocation
                ]
                self._api('org.setSystemEntitlements', *params)
            # Add software entitlements
            ch_families = ['rhel-server', 'rhel-server-6', 'rhel-server-7', 'rhel-client', 'rhel-client-6', 'rhel-client-7']
            for chf in ch_families:
                params = [
                    org['id'],   # orgId
                    chf,   # label
                    1   # allocation
                ]
                self._api('org.setSoftwareEntitlements', *params)
            # Store id of organization created
            self.created.append(org['id'])

        logger.info("As of now, we are going to work with first of created orgs only")
        self._logout()
        self.username = self.org_admin
        self.password = self.org_pass
        self._login()

        logger.info("Creating users")
        for i in range(100):
            params = [
                'benchmark-org-0-user-%s' % i,   # desiredLogin
                'benchmark-org-0-pass-%s' % i,   # desiredPassword
                'Us%s' % i,   # firstName
                'Er%s' % i,   # lastName
                'root@localhost',   # email
                0   # usePamAuth
            ]
            self._api('user.create', *params)

        logger.info("Creating channels")
        for i in range(100):
            params = [
                'benchmark-org-0-channel-%s' % i,   # label
                'benchmark-org-0-channel-%s' % i,   # name
                'benchmark-org-0-channel-%s' % i,   # summary
                'channel-x86_64',   # archLabel
                '',   # parentLabel
                'sha256',   # checkSumType
                {'url': 'https://www.example.com/security/fd431d51.txt', 'id': 'FD431D51', 'fingerprint': '567E 347A D004 4ADE 55BA 8A5F 199E 2F91 FD43 1D51'}   # gpgKey
            ]
            self._api('channel.software.create', *params)

        logger.info("Pushing packages into first of created channel")
        for i in range(500):
            for v in ['0.1', '0.2']:
                command = [
                    'rhnpush',
                    '--server',
                    'http://%s/APP' % self.hostname,
                    '-u',
                    self.username,
                    '-p',
                    self.password,
                    '-c',
                    self.org_channel,
                    '--nosig',
                    'test-rpmbuild-benchmark-org-0-package-%s-%s-1/RPMS/x86_64/benchmark-org-0-package-%s-%s-1.x86_64.rpm' % (i, v, i, v),
                ]
                rc = subprocess.call(command)
                assert rc == 0

        logger.info("Creating erratas")

        def get_pid_by_name(n, e, v, r, a):
            """Return package ID for given package
               name+epoch+version+release+arch"""
            params = [
                n,   # name
                v,   # version
                r,   # release
                e,   # epoch
                a   # archLabel
            ]
            return self._api('packages.findByNvrea', *params)[0]['id']

        for i in range(200):
            pid = get_pid_by_name('benchmark-org-0-package-%s' % i, '', '0.2', '1', 'x86_64')
            errata = {
                'synopsis': 'Fake advisory in org 0 channel 0 for package %i' % i,
                'advisory_name': 'benchmark-org-0-channel-0-package-%s' % i,
                'advisory_release': 1,
                'advisory_type': 'Bug Fix Advisory',
                'product': 'Fake product',
                'errataFrom': '11/18/16',
                'topic': 'topic',
                'description': 'description',
                'references': 'references',
                'notes': 'notes',
                'solution': 'solution',
            }
            bugs = [{'id': 1234567, 'summary': 'bug summary'}]
            keywords = ['benchmark']
            params = [
                errata,   # errata info
                bugs,   # bugs
                keywords,   # keywords
                [pid],   # packageIds
                True,   # publish
                [self.org_channel]   # ChannelLabeles
            ]
            self._api('errata.create', *params)

        logger.info("Creating activation key")
        for i in range(100):
            params = [
                '',   # key
                'Benchmark AK %s' % i,   # description
                'benchmark-org-0-channel-%s' % i,   # baseChannelLabel
                [],   # add-on entitlements
                False,   # universalDefault
            ]
            activationkey = self._api('activationkey.create', *params)
            if i == 0:
                ak = activationkey

        logger.info("Registering hosts")
        packages = []
        for i in range(950):   # some random packages just to get some payload
            packages.append({'name': 'package%s' % i,
                             'version': '1.2',
                             'release': '3',
                             'epoch': '',
                             'arch': 'x86_64'})
        for i in range(50):   # packages to make erratas applicable
            packages.append({'name': 'benchmark-org-0-package-%s' % i,
                             'version': '0.1',
                             'release': '1',
                             'epoch': '',
                             'arch': 'x86_64'})
        server_url = "https://%s/XMLRPC" % self.hostname
        client = xmlrpc_login(server_url)
        for i in range(1000):
            new_system = client.registration.new_system_user_pass(
                'System %s' % i,
                'RHEL Server',
                '6Server',
                'x86_64',
                self.username,
                self.password,
                {'packages': packages, 'token': ak})
            client.registration.refresh_hw_profile(
                new_system['system_id'],
                self.hwinfo)
        logger.info("Created organizations: %s" % ','.join(self.created))
        return self.created

    def cleanup(self, orgs):
        """Cleanup all the setup we did in setup()"""
        logger.info("Deleting organizations %s" % orgs)
        for i in orgs:
            self._api('org.delete', i)
        logger.info("Removing rpmfluff build directories")
        for f in os.listdir('.'):
            if re.search('test-rpmbuild-.*', f):
                shutil.rmtree(f)
        logger.info("Cleanup finished")

    def run(self):
        """Run the API benchmark"""
        # This part runs with Satellite admin user
        orgs = self._measure(self.repeats_default, 'org.listOrgs')
        swe = self._measure(self.repeats_default, 'org.listSoftwareEntitlements')
        sye = self._measure(self.repeats_default, 'org.listSystemEntitlements')
        orgid = None
        for org in orgs:
            odetail = self._measure(1, 'org.getDetails', org['name'])
            if org['name'] == 'benchmark-org-0':
                orgid = org['id']
                break
        users = self._measure(self.repeats_default, 'org.listUsers', orgid)
        # Below part runs with Org admin user
        self._logout()
        self.username = self.org_admin
        self.password = self.org_pass
        self._login()
        # Users
        users = self._measure(self.repeats_default, 'user.listUsers')
        for user in users:
            udetail = self._measure(1, 'user.getDetails', user['login'])
        channels = self._measure(self.repeats_default, 'channel.listSoftwareChannels')
        for channel in channels:
            chdetail = self._measure(1, 'channel.software.getDetails', channel['label'])
        # Packages
        packages = self._measure(self.repeats_default, 'channel.software.listAllPackages', self.org_channel)
        for package in packages:
            pdetail = self._measure(1, 'packages.getDetails', package['id'])
        # Errata
        erratas = self._measure(self.repeats_default, 'channel.software.listErrata', self.org_channel)
        for errata in erratas:
            edetail = self._measure(1, 'errata.getDetails', errata['advisory_name'])
        # Systems
        systems = self._measure(self.repeats_default, 'system.listSystems')
        for system in systems:
            sdetail = self._measure(1, 'system.getDetails', system['id'])
            sapplicable = self._measure(1, 'system.getUnscheduledErrata', system['id'])
        return self.actions

    def _api(self, method, *args):
        logger.debug("Running unmeasured API call %s %s", method, args)
        fce = getattr(self.client, method)
        return fce(self.key, *args)

    def _measure(self, repeats, method, *args):
        """Run given API call, measure its duration and record
           its measurement"""
        logger.debug("Running measured API call %s %s with %s repeats",
                     method, args if method != 'auth.login' else '(xxx)',
                     repeats)
        fce = getattr(self.client, method)
        start = time.time()
        for i in range(repeats):
            if self.key:
                output = fce(self.key, *args)
            else:
                output = fce(*args)
        end = time.time()
        self.actions.append({'repeats': repeats,
                             'method': method,
                             'args': args,
                             'output_len': len(output),
                             'start': start,
                             'end': end})
        return output

    def _login(self):
        """Populate self.key"""
        logger.info("Logging in to %s as %s", self.hostname, self.username)
        server_url = "https://%s/rpc/api" % self.hostname
        self.client = xmlrpc_login(server_url)
        logger.debug("Getting API key")
        self.key = self._measure(self.repeats_default, 'auth.login', self.username, self.password)

    def _logout(self):
        """Close the API session"""
        logger.info("Logging out")
        self._api('auth.logout')
        self.key = None
