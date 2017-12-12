"""Tests for loading LabJack Modbus Map Markup notation modbus maps.

@author Sam Pottinger
@license GNU GPL v2
"""

import os

import unittest

import ljmmm


# TODO: This is still somewhat incomplete
class LJMMMTests(unittest.TestCase):
    """Test case for reading LabJack Modbus Map Markup notation maps."""

    def assertIterableContentsEqual(self, l1, l2):
        """Utility function to check that two iterables have equal contents."""
        self.assertEqual(len(l1), len(l2))
        for item in l1:
            self.assertIn(item, l2)

    def test_generate_int_enumeration(self):
        """Test generating strings through numerical enumeration."""
        default_interval = ljmmm.generate_int_enumeration(
            ("test#", 1, 5, "", ""))
        custom_interval = ljmmm.generate_int_enumeration(
            ("test#", 0, 4, 2, ""))

        expected_default_interval = ["test#1", "test#2", "test#3", "test#4",
            "test#5"]
        self.assertIterableContentsEqual(default_interval,
            expected_default_interval)

        expected_custom_interval = ["test#0", "test#2", "test#4"]
        self.assertIterableContentsEqual(custom_interval,
            expected_custom_interval)

    def test_ljmmm_enumeration_field(self):
        """Test ljmmm string generation through numerical enumeration."""
        expected = ["test0_test", "test2_test", "test4_test"]
        ljmmm_src = "test#(0:4:2)_test"
        result = ljmmm.interpret_ljmmm_field(ljmmm_src)
        self.assertIterableContentsEqual(result, expected)

    def test_ljmmm_pound(self):
        """Test ljmmm field with a pound character."""
        ljmmm_src = "test#pound#(0:4:2)"
        result = ljmmm.interpret_ljmmm_field(ljmmm_src)
        expected = ["test#0", "test#2", "test#4"]
        self.assertEqual(result, expected)

    def test_enumerate_addresses(self):
        """Test generating modbus addresses based on a datatype size."""
        expected = [1000, 1002, 1004, 1006, 1008]
        result = ljmmm.enumerate_addresses(1000, 4, 2)
        self.assertIterableContentsEqual(result, expected)

    def test_interpret_firmwawre(self):
        """Test interpreting the availability of a register on a device."""
        expected_implicit = {"device": "test1", "fwmin": 0}
        expected_explicit = {"device": "test2", "fwmin": 0.5}
        implicit = ljmmm.interpret_firmware("test1")
        explicit = ljmmm.interpret_firmware(expected_explicit)
        self.assertDictEqual(implicit, expected_implicit)
        self.assertDictEqual(explicit, expected_explicit)

    def test_invalid_firmware(self):
        """Test interpreting an invalid firmware description."""
        with self.assertRaises(TypeError):
            ljmmm.interpret_firmware(5)

    def test_parse_register_data_expand(self):
        """Test expanding a sample ljmmm register description."""
        expected = [
            {
                "address": 2000,
                "name": "FIO0",
                "type": "UINT16",
                "type_index":"0",
                "devices":[
                    {"device":"U3", "fwmin":0},
                    {"device":"U6", "fwmin":0},
                    {"device":"T7", "fwmin":0.80},
                    {"device":"UE9", "fwmin":0}
                ],
                "readwrite": {"read": True, "write": True},
                "tags": ["DIO"],
                "description": "test",
                "constants": [],
                "streamable": False,
                "default": None,
                "isBuffer": False,
                "altnames": ["DIO0", "TEST0"],
            },
            {
                "address": 2001,
                "name": "FIO1",
                "type": "UINT16",
                "type_index":"0",
                "devices":[
                    {"device":"U3", "fwmin":0},
                    {"device":"U6", "fwmin":0},
                    {"device":"T7", "fwmin":0.80},
                    {"device":"UE9", "fwmin":0}
                ],
                "readwrite": {"read": True, "write": True},
                "tags": ["DIO"],
                "description": "test",
                "constants": [],
                "streamable": False,
                "default": None,
                "isBuffer": False,
                "altnames": ["DIO1", "TEST1"],
            },
            {
                "address": 2002,
                "name": "FIO2",
                "type": "UINT16",
                "type_index":"0",
                "devices":[
                    {"device":"U3", "fwmin":0},
                    {"device":"U6", "fwmin":0},
                    {"device":"T7", "fwmin":0.80},
                    {"device":"UE9", "fwmin":0}
                ],
                "readwrite": {"read": True, "write": True},
                "tags": ["DIO"],
                "description": "test",
                "constants": [],
                "streamable": False,
                "default": None,
                "isBuffer": False,
                "altnames": ["DIO2", "TEST2"],
            },
        ]

        result = ljmmm.parse_register_data(
            {
                "address":2000,
                "name":"FIO#(0:2)",
                "type":"UINT16",
                "devices":[
                    "U3",
                    "U6",
                    {"device":"T7", "fwmin":0.80},
                    "UE9"
                ],
                "readwrite":"RW",
                "tags":["DIO"],
                "altnames":["DIO#(0:2)", "TEST#(0:2)"],
                "description": "test"
            },
            expand_names = True
        )

        self.assertIterableContentsEqual(expected, result)

    def test_parse_register_data_expand_with_nothing_to_expand(self):
        expected = [
            {
                "address": 5010,
                "name": "SPI_DATA_TX",
                "type": "BYTE",
                "type_index":"99",
                "devices":[
                    {"device":"T7", "fwmin":0.80},
                ],
                "readwrite": {"read": False, "write": True},
                "tags": ["SPI"],
                "description": "test",
                "constants": [],
                "streamable": False,
                "default": None,
                "isBuffer": True,
                "altnames": ["SPI_DATA_WRITE"],
            },
        ]

        result = ljmmm.parse_register_data(
            {
                "address":5010,
                "name":"SPI_DATA_TX",
                "type":"BYTE",
                "devices":[
                    {"device":"T7", "fwmin":0.80},
                ],
                "readwrite":"W",
                "tags":["SPI"],
                "altnames":["SPI_DATA_WRITE"],
                "description": "test",
                "isBuffer": True,
            },
            expand_names = False
        )

        self.assertIterableContentsEqual(expected, result)


    def test_parse_register_data_compressed(self):
        """Test parsing a sample ljmmm register description."""

        # Jeez. I should make this test less fragile.
        EXTLINK_ICON = '<img style="margin-right: -1;" src="https://ljsimpleregisterlookup.herokuapp.com/static/images/ui-icons-extlink.png" />'

        expected = [
            {
                "address": 2000,
                "name": "FIO#(0:2)",
                "type": "UINT16",
                "type_index":"0",
                "devices":[
                    {"device":"U3", "fwmin":0},
                    {"device":"U6", "fwmin":0},
                    {"device":"T7", "fwmin":0.80},
                    {"device":"UE9", "fwmin":0}
                ],
                "readwrite": {"read": True, "write": True},
                "tags": ["DIO"],
                "description": "test <a target=\"_blank\" href=\"https://labjack.com/support/\">https://labjack.com/support/</a>%s. <a target=\"_blank\" href=\"http://imgur.com/gallery/zwK7XG6\">http://imgur.com/gallery/zwK7XG6</a>%s, end." %
                    (EXTLINK_ICON, EXTLINK_ICON),
                "constants": [],
                "streamable": False,
                "default": None,
                "isBuffer": False,
                "altnames": ["DIO#(0:2)", "TEST#(0:2)"],
            },
        ]

        result = ljmmm.parse_register_data(
            {
                "address":2000,
                "name":"FIO#(0:2)",
                "type":"UINT16",
                "devices":[
                    "U3",
                    "U6",
                    {"device":"T7", "fwmin":0.80},
                    "UE9"
                ],
                "readwrite":"RW",
                "tags":["DIO"],
                "altnames":["DIO#(0:2)", "TEST#(0:2)"],
                "description": "test https://labjack.com/support/. http://imgur.com/gallery/zwK7XG6, end."
            },
            expand_names = False
        )

        self.assertIterableContentsEqual(expected, result)


    def test_description_with_dots_should_not_yield_links(self):
        expected = [{
            "address":60662,
            "name":"FILE_IO_LUA_SWITCH_FILE",
            "type":"UINT32",
            "type_index":"1",
            "devices":[
                {"device":"T7", "fwmin":1.0168}
            ],
            "readwrite": {"read": True, "write": True},
            "tags":["LUA", "FILE_IO"],
            "description":"Write any value to this register to instruct Lua scripts to switch to a new file. Lua script should periodically check LJ.CheckFileFlag() to receive instruction, then call LJ.ClearFileFlag() after file switch is complete. Useful for applications that require continuous logging in a Lua script, and on-demand file access from a host.",
            "constants": [],
            "streamable": False,
            "default": None,
            "isBuffer": False,
            "altnames": [],
        }]

        result = ljmmm.parse_register_data({
            "address":60662,
            "name":"FILE_IO_LUA_SWITCH_FILE",
            "type":"UINT32",
            "devices":[
                {"device":"T7", "fwmin":1.0168}
            ],
            "readwrite":"RW",
            "tags":["LUA", "FILE_IO"],
            "description":"Write any value to this register to instruct Lua scripts to switch to a new file. Lua script should periodically check LJ.CheckFileFlag() to receive instruction, then call LJ.ClearFileFlag() after file switch is complete. Useful for applications that require continuous logging in a Lua script, and on-demand file access from a host."
        })

        self.assertIterableContentsEqual(expected, result)

        self.assertEqual(1, len(ljmmm.FIND_URLS.findall('this desc has website.org as the single link')))
        self.assertEqual(1, len(ljmmm.FIND_URLS.findall('this desc has website.co.uk as the single link')))
        self.assertEqual(1, len(ljmmm.FIND_URLS.findall('this desc has website.net as the single link')))
        self.assertEqual(1, len(ljmmm.FIND_URLS.findall('this desc has website.edu as the single link')))
        self.assertEqual(1, len(ljmmm.FIND_URLS.findall('this desc has website.gov as the single link')))
        self.assertEqual(0, len(ljmmm.FIND_URLS.findall('this desc has website.fake as the not a link')))
        self.assertEqual(0, len(ljmmm.FIND_URLS.findall('this desc has https://labjack.nope as the not a link')))


    def test_get_device_modbus_maps(self):
        EXPECTED_MAPS = {
            'T7': [
                (
                    {
                        'name': 'LED_COMM',
                        'tags': ['DIO'],
                        'readwrite': 'RW',
                        'devices': [
                            {'device': 'T7', 'fwmin': 1.7777},
                            {'device': 'T4', 'fwmin': 1.4444}
                        ],
                        'default': 0,
                        'address': 2990,
                        'type': 'UINT16',
                        'constants': [
                            {'name': 'Off', 'value': 0},
                            {'name': 'On', 'value': 1}
                        ],
                        'description': 'Sets the state of the COMM LED when the LEDs are set to manual, see the POWER_LED register.'
                    },
                    {
                        'streamable': False,
                        'description': 'Sets the state of the COMM LED when the LEDs are set to manual, see the POWER_LED register.',
                        'fwmin': 1.7777,
                        'tags': ['DIO'],
                        'default': 0,
                        'deviceDescription': '',
                        'altnames': [],
                        'write': True,
                        'type_index': '0',
                        'read': True,
                        'constants': [
                            {'name': 'Off', 'value': 0},
                            {'name': 'On', 'value': 1}
                        ],
                        'address': 2990,
                        'type': 'UINT16',
                        'isBuffer': False,
                        'name': 'LED_COMM'
                    }
                )
            ],
            'T4': [
                (
                    {
                        'name': 'LED_COMM',
                        'tags': ['DIO'],
                        'readwrite': 'RW',
                        'devices': [
                            {'device': 'T7', 'fwmin': 1.7777},
                            {'device': 'T4', 'fwmin': 1.4444}
                        ],
                        'default': 0,
                        'address': 2990,
                        'type': 'UINT16',
                        'constants': [
                            {'name': 'Off', 'value': 0},
                            {'name': 'On', 'value': 1}
                        ],
                        'description': 'Sets the state of the COMM LED when the LEDs are set to manual, see the POWER_LED register.'
                    },
                    {
                        'streamable': False,
                        'description': 'Sets the state of the COMM LED when the LEDs are set to manual, see the POWER_LED register.',
                        'fwmin': 1.4444,
                        'tags': ['DIO'],
                        'default': 0,
                        'deviceDescription': '',
                        'altnames': [],
                        'write': True,
                        'type_index': '0',
                        'read': True,
                        'constants': [
                            {'name': 'Off', 'value': 0},
                            {'name': 'On', 'value': 1}
                        ],
                        'address': 2990,
                        'type': 'UINT16',
                        'isBuffer': False,
                        'name': 'LED_COMM'
                    }
                )
            ]
        }

        maps = ljmmm.get_device_modbus_maps(
            src=os.path.join(os.path.split(os.path.realpath(__file__))[0], "ljmmm_test.json"),
            expand_names=True,
            inc_orig=True
        )
        self.assertEqual(EXPECTED_MAPS, maps)


if __name__ == "__main__":
    unittest.main()
