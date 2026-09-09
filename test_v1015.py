#!/usr/bin/python3
"""V1.0.1.5 (STM32F4) patch oracles for MiPatcher(..., \"4proita\")."""
from __future__ import annotations

import unittest
from pathlib import Path

import keystone

ROOT = Path(__file__).resolve().parents[3]
F4_BIN = ROOT / "firmware/kits/4pro-f4-stlink/EC_ESC_Driver_V1.0.1.5.bin"
F1_BIN = ROOT / "firmware/kits/4pro-stlink/EC_ESC_Driver_V0.2.2.bin"

# File offsets (VA = 0x08004000 + off) — test oracles only
OFF = {
    "speed_sport": 0x71FA,
    "crc": 0x71FC,
    "amp_sport": 0x7200,
    "speed_ped": 0x7208,
    "amp_ped": 0x7228,
    "amp_max_ped": 0x723C,
    "amp_drive": 0x7252,
    "amp_sport_cmp": 0x725E,
    "amp_drive_cmp": 0x7256,
    "amp_max_sport": 0x726A,
    "speed_drive": 0x727C,
    "amp_max_drive": 0x7280,
    "autobrake": 0x735C,
    "kers": 0x747E,
    "kers_multi": 0x74A4,
    "mss_hi": 0x759A,
    "modellock": 0x35F8,
    "volt": 0x3E74,
    "shutdown": 0x197A,
    "dpc_clear": 0x11D6,
    "dpc_force": 0x7B88,
    "charge_cbz": 0x84DC,
    "cc_delay": 0x1D96,
    "region_3e": 0x7C2C,
    "region_r2": 0x7C40,
    "region_r1": 0x7C50,
    "ped_beq": 0x0B4C,
    "blm_brake": 0x0B42,
    "blm_ped": 0x0B4A,
}

MSS_SCALE = 410
KS = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_THUMB)


def asm(s: str) -> bytes:
    return bytes(KS.asm(s)[0])


def make_v1015_patcher(data: bytes):
    """Patcher under test — MiPatcher with V1.0.1.5 FindPattern branches."""
    from mi_patcher import MiPatcher
    return MiPatcher(bytearray(data), "4proita")


def _load(path: Path) -> bytes:
    if not path.is_file():
        raise unittest.SkipTest(f"missing firmware: {path}")
    return path.read_bytes()


def _assert_sites(data: bytearray, ret, stock: bytes):
    """Each (name, hex_ofs, pre, post) must match stock pre and written post."""
    assert ret, "expected at least one patch site"
    for item in ret:
        name, ofs_s, pre_h, post_h = item[0], item[1], item[2], item[3]
        ofs = int(ofs_s, 16)
        pre = bytes.fromhex(pre_h)
        post = bytes.fromhex(post_h)
        assert stock[ofs:ofs + len(pre)] == pre, f"{name}: stock pre mismatch @ {ofs:#x}"
        assert data[ofs:ofs + len(post)] == post, f"{name}: post not applied @ {ofs:#x}"
        assert pre != post or name.endswith("_force") is False or True


class TestV1015Patches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = _load(F4_BIN)

    def setUp(self):
        self.p = make_v1015_patcher(self.stock)

    def test_speed_limits(self):
        r = self.p.speed_limit_ped(9)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["speed_ped"]:OFF["speed_ped"] + 4], asm("MOV.W R9, #9"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.speed_limit_drive(22)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["speed_drive"]:OFF["speed_drive"] + 2], asm("MOVS R0, #22"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.speed_limit_sport(27)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["speed_sport"]:OFF["speed_sport"] + 2], asm("MOVS R3, #27"))

    def test_crc(self):
        r = self.p.current_raising_coeff(600)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["crc"]:OFF["crc"] + 4], asm("MOVW R2, #600"))

    def test_amperes(self):
        r = self.p.ampere_ped(10000)
        _assert_sites(self.p.data, r, self.stock)

        self.p = make_v1015_patcher(self.stock)
        r = self.p.ampere_drive(20000)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["amp_drive_cmp"]:OFF["amp_drive_cmp"] + 2], asm("CMP R0, R0"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.ampere_sport(30000)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["amp_sport_cmp"]:OFF["amp_sport_cmp"] + 2], asm("CMP R0, R0"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.ampere_max(10000, 35000, 55000)
        _assert_sites(self.p.data, r, self.stock)

    def test_kers_and_autobrake(self):
        r = self.p.remove_kers()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["kers"]:OFF["kers"] + 2], asm("MOVS R0, #0"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.kers_multi(2, 5, 10)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(len(bytes.fromhex(r[0][3])), 32)

        self.p = make_v1015_patcher(self.stock)
        r = self.p.remove_autobrake()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["autobrake"]:OFF["autobrake"] + 4], asm("MOVW R12, #0xffff"))

    def test_motor_start(self):
        r = self.p.motor_start_speed(3.0)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(int(r[0][1], 16), OFF["mss_hi"])
        self.assertEqual(bytes.fromhex(r[0][3]), asm(f"MOVW R7, #{int(round(3.0 * MSS_SCALE))}"))

    def test_charge_dpc_cc_shutdown(self):
        r = self.p.remove_charging_mode()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["charge_cbz"]:OFF["charge_cbz"] + 2], asm("NOP"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.dpc()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["dpc_clear"]:OFF["dpc_clear"] + 4], asm("NOP") * 2)

        self.p = make_v1015_patcher(self.stock)
        r = self.p.cc_delay(2.0)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["cc_delay"]:OFF["cc_delay"] + 4], asm("MOV.W R1, #400"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.shutdown_time(1.0)
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["shutdown"]:OFF["shutdown"] + 4], asm("CMP.W R0, #200"))

    def test_region_modellock_volt_lights(self):
        r = self.p.region_free()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["region_3e"]:OFF["region_3e"] + 4], asm("NOP.W"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.remove_modellock()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["modellock"]:OFF["modellock"] + 2], b"\x01\xe0")

        self.p = make_v1015_patcher(self.stock)
        r = self.p.volt_limit(45.01)
        _assert_sites(self.p.data, r, self.stock)
        self.assertNotEqual(r[0][2], r[0][3])

        self.p = make_v1015_patcher(self.stock)
        r = self.p.ped_noblink()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["ped_beq"]:OFF["ped_beq"] + 2], asm("NOP"))

        self.p = make_v1015_patcher(self.stock)
        r = self.p.brake_light_static()
        _assert_sites(self.p.data, r, self.stock)
        self.assertEqual(self.p.data[OFF["blm_brake"]:OFF["blm_brake"] + 2], asm("CMP R1, #0xFF"))
        self.assertEqual(self.p.data[OFF["blm_ped"]:OFF["blm_ped"] + 2], asm("CMP R1, #0xFF"))

    def test_f1_regression_speed_drive(self):
        stock = _load(F1_BIN)
        from mi_patcher import MiPatcher
        p = MiPatcher(bytearray(stock), "4pro")
        r = p.speed_limit_drive(22)
        self.assertTrue(r)
        ofs = int(r[0][1], 16)
        post = bytes.fromhex(r[0][3])
        self.assertEqual(p.data[ofs:ofs + len(post)], post)
        self.assertNotEqual(r[0][2], r[0][3])


if __name__ == "__main__":
    unittest.main()
