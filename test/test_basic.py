""" Darp tests """

import unittest

import darp
from darp.arp_scan import ArpScan
from darp.db import DBWrapper
from darp.diff import ScanDiff
from darp.helpers import get_safe_timestamp


class ArpScanTestCase(unittest.TestCase):
    """ Test case for ArpScan class """

    def setUp(self):
        pass

    def test_parse(self):
        """ Tests the parse function of the ArpScan class in arp_scan module """
        example_arp_scan_out = "\n".join([
            "Interface: en0, datalink type: EN10MB (Ethernet)",
            "Starting arp-scan 1.9 with 256 hosts (http://www.nta-monitor.com/tools/arp-scan/)",
            "10.1.1.1	aa:bb:cc:dd:ee:ff	(Unknown)",
            "10.1.1.10	bb:cc:dd:ee:ff:aa	Apple, Inc",
            "",
            "524 packets received by filter, 0 packets dropped by kernel",
            "Ending arp-scan 1.9: 256 hosts scanned in 1.776 seconds (144.14 hosts/sec). "\
            + "2 responded",
        ])
        test_parsed = ArpScan.parse(example_arp_scan_out)
        expected_parsed = {
            'devices': [
                {'address': '10.1.1.1',
                'mac': 'aa:bb:cc:dd:ee:ff',
                'name': '(Unknown)'},
                {'address': '10.1.1.10',
                'mac': 'bb:cc:dd:ee:ff:aa',
                'name': 'Apple, Inc'}
            ],
            'interface': 'en0'
        }
        self.assertEquals(test_parsed, expected_parsed)

class DBWrapperTestCase(unittest.TestCase):
    """ Test case for DBWrapper class in db module """
    def setUp(self):
        self.dbwrapper = DBWrapper("darp_db_test.json")
        self.dbwrapper.purge()
        self.stamp = '2016-11-5_11-53-00'
        self.mac = 'aa:bb:cc:dd:ee:ff'
        self.name = '(Unknown)'
        self.sighting = dict(
            name=self.name,
            address="10.1.1.1",
            mac=self.mac,
            stamp=self.stamp
        )
        self.dbwrapper.insert_sighting(
            **self.sighting
        )

    def testLastSighting(self):
        stamp = self.dbwrapper.last_sighting(self.mac).get('stamp')
        expected_stamp = self.stamp
        self.assertEqual(stamp, expected_stamp)

        stamp = self.dbwrapper.last_sighting("ff:ff:ff:ff:ff:ff")
        expected_stamp = None
        self.assertEqual(stamp, expected_stamp)

    def testStampedSightings(self):
        sightings = self.dbwrapper.stamped_sightings(self.stamp)
        expected_sightings = [self.sighting]
        self.assertEquals(sightings, expected_sightings)
        # expected_sightings =

    def testLatestScan(self):
        latest_scan = self.dbwrapper.latest_scan()
        expected_latest_scan = [{u'stamp': u'2016-11-5_11-53-00', u'mac': u'aa:bb:cc:dd:ee:ff', u'name': u'(Unknown)', u'address': u'10.1.1.1'}]
        self.assertEquals(latest_scan, expected_latest_scan)

    def testLastName(self):
        self.assertEqual(
            self.dbwrapper.last_name(self.mac),
            self.name
        )

        new_name = "new name"
        self.dbwrapper.insert_sighting(
            name=new_name,
            address="10.1.1.1",
            mac=self.mac,
            stamp=get_safe_timestamp()
        )

        self.assertEqual(
            self.dbwrapper.last_name(self.mac),
            new_name
        )

    def testOwner(self):
        mac_b = "ff:aa:bb:cc:dd:ee"

        self.dbwrapper.insert_sighting(
            name="(Unknown)",
            address="10.1.1.2",
            mac=mac_b,
            stamp=get_safe_timestamp()
        )

        owner_a = "Owner A"
        owner_b = "Owner B"
        self.dbwrapper.set_owner(self.mac, owner_a)
        self.dbwrapper.set_owner(mac_b, owner_b)

        self.assertEqual(
            self.dbwrapper.get_owner(self.mac),
            owner_a
        )

        self.assertEqual(
            self.dbwrapper.get_owner(mac_b),
            owner_b
        )

class ScanDiffTestCase(unittest.TestCase):
    """ Test case for ScanDiff class in diff module """
    def setUp(self):
        self.old_scan = [
            {'address': '10.1.1.1',
            'mac': 'aa:bb:cc:dd:ee:ff',
            'name': '(Unknown)'},
            {'address': '10.1.1.10',
            'mac': 'bb:cc:dd:ee:ff:aa',
            'name': 'Apple, Inc'}
        ]
        self.new_scan = [
            {'address': '10.1.1.1',
            'mac': 'aa:bb:cc:dd:ee:ff',
            'name': '(Unknown)'},
            {'address': '10.1.1.12',
            'mac': 'cc:dd:ee:ff:aa:bb',
            'name': 'SAMSUNG ELECTRO-MECHANICS CO., LTD. (DUP: 1)'}
        ]
        self.diff = ScanDiff(self.old_scan, self.new_scan)

    def testMacDifference(self):
        added, removed = self.diff.mac_difference()
        expected_added = ['cc:dd:ee:ff:aa:bb']
        expected_removed = ['bb:cc:dd:ee:ff:aa']
        self.assertEquals(added, expected_added)
        self.assertEquals(removed, expected_removed)


if __name__ == '__main__':
    unittest.main()
