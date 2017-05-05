"""Tests for loading LabJack Modbus Map Markup notation modbus maps.

@author Sam Pottinger
@license GNU GPL v2
"""

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
                "isBuffer": False
            },
            {
                "address": 2001,
                "name": "FIO1",
                "type": "UINT16",
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
                "isBuffer": False
            },
            {
                "address": 2002,
                "name": "FIO2",
                "type": "UINT16",
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
                "isBuffer": False
            },
                        {
                "address": 2000,
                "name": "DIO0",
                "type": "UINT16",
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
                "isBuffer": False
            },
            {
                "address": 2001,
                "name": "DIO1",
                "type": "UINT16",
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
                "isBuffer": False
            },
            {
                "address": 2002,
                "name": "DIO2",
                "type": "UINT16",
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
                "isBuffer": False
            }
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
                "altnames":["DIO#(0:2)"],
                "description": "test"
            },
            expand_names = True
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
                "isBuffer": False
            },
            {
                "address": 2000,
                "name": "DIO#(0:2)",
                "type": "UINT16",
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
                "isBuffer": False
            }
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
                "altnames":["DIO#(0:2)"],
                "description": "test https://labjack.com/support/. http://imgur.com/gallery/zwK7XG6, end."
            },
            expand_names = False
        )

        self.assertIterableContentsEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
