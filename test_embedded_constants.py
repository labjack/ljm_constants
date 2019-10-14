import os
import unittest
import subprocess

from labjack import ljm
import ljmmm
import generate_embedded_constants as genconsts

# Get the register directory and conflict directory data structures
# The register directory is a list of dictonaries. the dictionaries hold:
#   "crc": (crc32/POSIX)
#   "address": (index in conflict directory if there is a conflict)
#   "data_type": (if there is a conflict upper nibble is index location, 0xF if
#                no index, lower is conflict location)
#   "conflict_mode": (o if no conflict, 1 if there is a conflict)
#   "short_name": (register name without numbers)
# The conflict directory is a dictionary whose key is the register name and
# the "values" are dictonaries containing the register:
#   "conflict_num":
#   "address":
#   "data_type":
#   "conflict_mode":
#   "short_name":
  # "all_nums": (list of numbers found in the register name)

reg_dir, conflict_dir, num_dup_registers = genconsts.generate(False)
def generate_test_directories(test_registers, test_conflict_dir, test_reg_dir):
    test_dup_registers = 0
    for reg in test_registers:
        test_reg_dir, test_conflict_dir, test_dup_registers = genconsts.extract_reg_data(
            reg,
            test_reg_dir,
            test_conflict_dir,
            test_dup_registers
        )
    conflict_duplicates = 0
    test_conflict_dir, test_reg_dir, conflict_duplicates = genconsts.check_and_sort_registers(
        test_conflict_dir,
        test_reg_dir
    )
    test_dup_registers += conflict_duplicates
    return (test_conflict_dir, test_reg_dir, test_dup_registers)

class EmbeddedConstantsTests(unittest.TestCase):
    # Check crc related items
    def test_crc_val_correct(self):
        for reg in reg_dir:
            # Test a low crc number
            if (reg["short_name"] == "ONEWIRE_ROM_BRANCHS_FOUND_H"):
                self.assertEqual(reg["crc"], "0x00734919")

            if (reg["short_name"] == "STREAM_OUT_BUFFER_F"):
                self.assertEqual(reg["crc"], "0x4477BBF5")

            if (reg["short_name"] == "IC_DATA_TX"):
                self.assertEqual(reg["crc"], "0x02C958F4")

            if (reg["short_name"] == "AIN_BIN"):
                self.assertEqual(reg["crc"], "0x64EACE2A")

            if (reg["short_name"] == "DIO"):
                self.assertEqual(reg["crc"], "0x9B684F2B")

            # Test a high crc number
            if (reg["short_name"] == "IC_SDA_DIONUM"):
                self.assertEqual(reg["crc"], "0xFFEA11A5")

    def test_crc_order(self):
        last_crc = "0X00000000"
        for i in range(0,len(reg_dir)):
            crc_int = int(reg_dir[i]["crc"], 16)
            last_crc_int = int(last_crc, 16)
            if (crc_int < last_crc_int):
                bad_sort = True
                print("bad sort with these crc's:")
                print("\tlast: %s current: %s" % (last_crc, reg_dir[i]["crc"]))
            else:
                bad_sort = False
            self.assertFalse(bad_sort)
            last_crc = reg_dir[i]["crc"]

    def test_dup_crc_vals(self):
        for i in range(0,len(reg_dir)):
            if (i != 0):
                # Register directory is sorted by crc, so if there are
                # duplicate crc's they are next to each other
                self.assertNotEqual(reg_dir[i-1]["crc"], reg_dir[i]["crc"])

    # Check conflict and duplicate register detection
    def test_conflict_and_duplicate_detection(self):
        test_reg_dir = []
        test_conflict_dir = {}
        num_conflicts = 0
        test_registers = [
            {
                "name":"TEST(0:3)_INDEX_32",
                "address":42343,
                "type":"UINT16",
            },
            {
                "name":"TEST(4:9)_INDEX_32",
                "address":42344,
                "type":"UINT16",
            },
            {
                "name":"TEST(0:3)_INDEX_64",
                "address":43242,
                "type":"UINT16",
            },
            {
                "name":"TEST_64_INDEX(0:3)",
                "address":4324,
                "type":"UINT16",
            },
            {
                "name":"TEST_32_INDEX(0:3)",
                "address":4325,
                "type":"UINT16",
            },
            {
                "name":"TEST(0:3)",
                "address":1233,
                "type":"UINT16",
            },
            {
                "name":"TEST(4:9)",
                "address":1234,
                "type":"UINT16",
            },
            {
                "name":"TEST_F32",
                "address":1,
                "type":"UINT16",
            },
            {
                "name":"TEST_F64",
                "address":2,
                "type":"UINT16",
            },
            {
                "name":"2TEST_NAME",
                "address":5,
                "type":"UINT16",
            },
            {
                "name":"3TEST_NAME",
                "address":6,
                "type":"UINT16",
            },
            {
                "name":"TEST_A",
                "address":43,
                "type":"UINT16",
            },
            {
                "name":"TEST_B",
                "address":44,
                "type":"UINT16",
            },
            {
                "name":"TEST_C",
                "address":44,
                "type":"UINT16",
            },
            {
                "name":"TEST_C",
                "address":44,
                "type":"UINT16",
            },
        ]
        test_conflict_dir, test_reg_dir, test_dup_registers = generate_test_directories(
            test_registers,
            test_conflict_dir,
            test_reg_dir
        )
        for reg in test_reg_dir:
            if (reg["conflict_mode"] == 1):
                num_conflicts += 1
        self.assertEqual(num_conflicts, 4)
        self.assertEqual(len(test_conflict_dir), 4)
        self.assertEqual(len(test_reg_dir), 8)
        self.assertEqual(test_dup_registers, 3)

    # Check conflict dir size
    def test_conflict_dir_size(self):
        conflict_dir_size = 0
        for reg in reg_dir:
            if(reg["conflict_mode"] == 1):
                conflict_dir_size += 1
        self.assertEqual(conflict_dir_size, len(conflict_dir))

    # Check num registers size (num in register list and conflict tables)
    def test_num_registers(self):
        modbus_maps = ljmmm.get_device_modbus_maps(
        src='LabJack/LJM/ljm_constants.json',
        expand_names=False,
        expand_alt_names=True,
        remove_digit_reg=True,
        )
        all_reg_names = []
        for device in modbus_maps:
            for reg in modbus_maps[device]:
                name = reg["name"]
                if (not name in all_reg_names):
                    all_reg_names.append(name)
        new_num_registers = len(reg_dir) + num_dup_registers
        for table_name in conflict_dir:
            new_num_registers += len(conflict_dir[table_name])
        new_num_registers -= len(conflict_dir)
        self.assertEqual(new_num_registers, len(all_reg_names))

    # Check register addresses
    def test_conflict_reg_addresses(self):
        test_reg_dir = []
        test_conflict_dir = {}
        num_conflicts = 0
        test_registers = [
            {
                "name":"TEST_A",
                "address":0,
                "type":"UINT16",
            },
            {
                "name":"TEST_F32",
                "address":1,
                "type":"UINT16",
            },
            {
                "name":"TEST_F64",
                "address":2,
                "type":"UINT16",
            },
            {
                "name":"TEST_B(0:3)",
                "address":3,
                "type":"UINT16",
            },
            {
                "name":"TEST_B(4:7)",
                "address":4,
                "type":"UINT16",
            },
            {
                "name":"TEST1(0:3)",
                "address":5,
                "type":"UINT16",
            },
            {
                "name":"TEST1(4:7)",
                "address":6,
                "type":"UINT16",
            },
            {
                "name":"TESTH5(0:3)",
                "address":-9,
                "type":"UINT16",
            },
            {
                "name":"TESTG4(0:3)",
                "address":-9,
                "type":"UINT16",
            },
            {
                "name":"TESTF3(0:3)",
                "address":-9,
                "type":"UINT16",
            },
            {
                "name":"TESTE1(0:3)",
                "address":-9,
                "type":"UINT16",
            },
            {
                "name":"TESTD1(0:3)",
                "address":-9,
                "type":"UINT16",
            },
        ]
        test_conflict_dir, test_reg_dir, test_dup_registers = generate_test_directories(
            test_registers,
            test_conflict_dir,
            test_reg_dir
        )
        for reg in test_reg_dir:
            if (reg["short_name"] == "TEST_A"):
                self.assertEqual(reg["address"], 0)
            if (reg["short_name"] == "TEST_F"):
                self.assertEqual(reg["address"], 0)
            if (reg["short_name"] == "TEST_B"):
                self.assertEqual(reg["address"], 3)
            if (reg["short_name"] == "TEST"):
                self.assertEqual(reg["address"], 1)
            if (reg["short_name"] == "TESTD"):
                self.assertEqual(reg["address"], 6)
            if (reg["short_name"] == "TESTE"):
                self.assertEqual(reg["address"], 5)
            if (reg["short_name"] == "TESTF"):
                self.assertEqual(reg["address"], 4)
            if (reg["short_name"] == "TESTG"):
                self.assertEqual(reg["address"], 3)
            if (reg["short_name"] == "TESTH"):
                self.assertEqual(reg["address"], 2)
        for table_name in test_conflict_dir:
            table = test_conflict_dir[table_name]
            if (table_name == "TEST_F"):
                self.assertEqual(table[0]["address"], 1)
                self.assertEqual(table[1]["address"], 2)
            if (table_name == "TEST"):
                self.assertEqual(table[0]["address"], 5)

    # Check register data types
    def test_data_types(self):
        test_reg_dir = []
        test_conflict_dir = {}
        num_conflicts = 0
        test_registers = [
            {
                "name":"TEST_A",
                "address":0,
                "type":"UINT32",
            },
            {
                "name":"TEST_F32",
                "address":1,
                "type":"UINT16",
            },
            {
                "name":"TEST_F64",
                "address":2,
                "type":"UINT16",
            },
            {
                "name":"TEST_B(0:3)",
                "address":3,
                "type":"BYTE",
            },
            {
                "name":"TEST_B(4:7)",
                "address":4,
                "type":"BYTE",
            },
            {
                "name":"TEST1(0:3)",
                "address":5,
                "type":"FLOAT32",
            },
            {
                "name":"TEST1(4:7)",
                "address":6,
                "type":"FLOAT32",
            },
            {
                "name":"TEST1(0:3)_FB32",
                "address":7,
                "type":"STRING",
            },
            {
                "name":"TEST1(0:3)_FB64",
                "address":8,
                "type":"STRING",
            },
        ]
        test_conflict_dir, test_reg_dir, test_dup_registers = generate_test_directories(
            test_registers,
            test_conflict_dir,
            test_reg_dir
        )
        for reg in test_reg_dir:
            if (reg["short_name"] == "TEST_A"):
                self.assertEqual(reg["data_type"], 1)
            if (reg["short_name"] == "TEST_B"):
                self.assertEqual(reg["data_type"], 99)
            if (reg["short_name"] == "TEST_F"):
                self.assertEqual(reg["data_type"], "0xF0")
            if (reg["short_name"] == "TEST"):
                self.assertEqual(reg["data_type"], "0x10")
            if (reg["short_name"] == "TEST_FB"):
                self.assertEqual(reg["data_type"], "0x12")
        for table_name in test_conflict_dir:
            table = test_conflict_dir[table_name]
            if (table_name == "TEST_F"):
                self.assertEqual(table[0]["data_type"], 0)
                self.assertEqual(table[1]["data_type"], 0)
            if (table_name == "TEST"):
                self.assertEqual(table[0]["data_type"], 5)
            if (table_name == "TEST_FB"):
                self.assertEqual(table[0]["data_type"], 98)
                self.assertEqual(table[1]["data_type"], 98)

if __name__ == "__main__":
    unittest.main()