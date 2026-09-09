#!/usr/bin/python3
"""MiPatcher tests: README DRV smoke + V1.0.1.5 (4proita) oracles.

Repo firmware/ (preferred) plus optional roller archive:
  …/hax/roller/4_firmware/bins/DRV{016,017,242,245,247,248,252,319,321}.bin
  …/hax/roller/4_firmware/nu_bins/{drv022,4Pro_DRV022,4Plus_DRV0037}.bin

Still missing as plaintext ESC: DRV176.
DRV1415: converted from roller/0_legacy/drv1415.hex → firmware/fixtures/DRV1415.bin
(early Ninebot ES dump — MiPatcher sigs do not land; min_ok=0).

Xiaomi OTA MCU images under firmware/ota/xiaomi/ are a different format (no
Scooter_Mi* ESC header) and are inventoried here as non-MiPatcher targets.

V1.0.1.5 oracles: TestV1015Patches.
"""
from __future__ import annotations

import unittest
from pathlib import Path

import keystone

ROOT = Path(__file__).resolve().parents[3]
FW = ROOT / "firmware"
XIAOMI = FW / "ota" / "xiaomi"
F4_BIN = FW / "kits/4pro-f4-stlink/EC_ESC_Driver_V1.0.1.5.bin"
F1_BIN = FW / "kits/4pro-stlink/EC_ESC_Driver_V0.2.2.bin"
# Optional external archive (plaintext DRV*.bin collection).
ROLLER_BINS = Path(
    "/media/jethro/d07c3610-f34e-4f3e-ab08-baa62f0de2ab"
    "/jethro/workdir/hax/roller/4_firmware/bins"
)
ROLLER_NU = Path(
    "/media/jethro/d07c3610-f34e-4f3e-ab08-baa62f0de2ab"
    "/jethro/workdir/hax/roller/4_firmware/nu_bins"
)

# README “Supported DRVs” → MiPatcher model + candidate plaintext ESC paths.
# First existing file wins (repo firmware preferred, then roller archive).
DRV_MATRIX = [
    {
        "drv": "DRV016",
        "model": "mi3",
        "paths": [ROLLER_BINS / "DRV016.bin"],
        "min_ok": 15,
    },
    {
        "drv": "DRV017",
        "model": "mi3",
        "paths": [
            FW / "ota/ninebot/scooter.v7/EC_ESC_Driver_V0.1.7.bin",
            ROLLER_BINS / "DRV017.bin",
        ],
        "min_ok": 15,
    },
    {
        "drv": "DRV242",
        "model": "pro2",
        "paths": [ROLLER_BINS / "DRV242.bin"],
        "min_ok": 15,
    },
    {
        "drv": "DRV245",
        "model": "pro2",
        "paths": [
            FW / "ota/ninebot/scooter.v5/EC_ESC_Driver_V2.4.5.bin",
            ROLLER_BINS / "DRV245.bin",
        ],
        "min_ok": 15,
    },
    {
        "drv": "DRV247",
        "model": "pro2",
        "paths": [ROLLER_BINS / "DRV247.bin"],
        "min_ok": 15,
    },
    {
        "drv": "DRV248",
        "model": "pro2",
        "paths": [ROLLER_BINS / "DRV248.bin"],
        "min_ok": 15,
    },
    {
        "drv": "DRV252",
        "model": "pro2",
        "paths": [
            FW / "ota/ninebot/scooter.v4/EC_ESC_Driver_V2.5.2.bin",
            FW / "fixtures/EC_ESC_Driver_V2.5.2_decrypted.bin",
            ROLLER_BINS / "DRV252.bin",
        ],
        "min_ok": 15,
    },
    {
        "drv": "DRV319",
        "model": "1s",
        "paths": [ROLLER_BINS / "DRV319.bin"],
        "min_ok": 15,
    },
    {
        "drv": "DRV321",
        "model": "1s",
        "paths": [
            FW / "ota/ninebot/scooter.v3/EC_ESC_Driver_V3.2.1.bin",
            ROLLER_BINS / "DRV321.bin",
        ],
        "min_ok": 15,
    },
    {
        "drv": "DRV022",
        "model": "4pro",
        "paths": [
            FW / "ota/ninebot/scooter.v8/EC_ESC_Driver_V0.2.2.bin",
            FW / "kits/4pro-stlink/EC_ESC_Driver_V0.2.2.bin",
            ROLLER_NU / "drv022.bin",
            ROLLER_NU / "4Pro_DRV022.bin",
        ],
        "min_ok": 15,
        "experimental": True,
    },
    {
        "drv": "DRV0037",
        "model": "4pro",
        "paths": [
            FW / "ota/ninebot/scooter.v16/EC_ESC_Driver_V0.0.3.7.bin",
            ROLLER_NU / "4Plus_DRV0037.bin",
            ROLLER_NU / "4Max_DRV0037.bin",
        ],
        "min_ok": 1,
        "experimental": True,
    },
    {
        "drv": "DRV176",
        "model": "1s",
        "paths": [],  # not in roller bins/
        "min_ok": 15,
        "experimental": True,
    },
    {
        "drv": "DRV1415",
        "model": "1s",
        "paths": [
            FW / "fixtures/DRV1415.bin",  # from roller/0_legacy/drv1415.hex
        ],
        # Early Ninebot ES (NineBotScooter / NBScooter0001) — not Scooter_Mi*.
        "min_ok": 0,
        "experimental": True,
    },
    {
        "drv": "EC_ESC_Driver_V1.0.1.5",
        "model": "4proita",
        "paths": [
            FW / "kits/4pro-f4-stlink/EC_ESC_Driver_V1.0.1.5.bin",
            FW / "ota/ninebot/scooter.15/EC_ESC_Driver_V1.0.1.5.bin",
        ],
        "min_ok": 15,
        "experimental": True,
    },
]


def _resolve(entry: dict) -> Path | None:
    for p in entry.get("paths") or []:
        if p is not None and Path(p).is_file():
            return Path(p)
    return None


def _assert_sites(data: bytearray, ret, stock: bytes, mod: str):
    assert ret, f"{mod}: empty result"
    for item in ret:
        name, ofs_s, pre_h, post_h = item[0], item[1], item[2], item[3]
        ofs = int(ofs_s, 16)
        pre = bytes.fromhex(pre_h)
        post = bytes.fromhex(post_h)
        assert stock[ofs:ofs + len(pre)] == pre, (
            f"{mod}/{name}: stock pre mismatch @ {ofs:#x}"
        )
        assert data[ofs:ofs + len(post)] == post, (
            f"{mod}/{name}: post not applied @ {ofs:#x}"
        )


def _core_mods(patcher):
    """Representative mods exercised across DRVs."""
    return [
        ("speed_limit_drive", lambda: patcher.speed_limit_drive(22)),
        ("speed_limit_sport", lambda: patcher.speed_limit_sport(27)),
        ("speed_limit_ped", lambda: patcher.speed_limit_ped(9)),
        ("remove_kers", lambda: patcher.remove_kers()),
        ("remove_autobrake", lambda: patcher.remove_autobrake()),
        ("remove_charging_mode", lambda: patcher.remove_charging_mode()),
        ("dpc", lambda: patcher.dpc()),
        ("cc_delay", lambda: patcher.cc_delay(2.0)),
        ("shutdown_time", lambda: patcher.shutdown_time(1.0)),
        ("volt_limit", lambda: patcher.volt_limit(45.01)),
        ("current_raising_coeff", lambda: patcher.current_raising_coeff(600)),
        ("motor_start_speed", lambda: patcher.motor_start_speed(3.0)),
        ("region_free", lambda: patcher.region_free()),
        ("remove_modellock", lambda: patcher.remove_modellock()),
        ("ped_noblink", lambda: patcher.ped_noblink()),
        ("brake_light_static", lambda: patcher.brake_light_static()),
        ("ampere_ped", lambda: patcher.ampere_ped(10000)),
        ("ampere_drive", lambda: patcher.ampere_drive(20000)),
        ("ampere_sport", lambda: patcher.ampere_sport(30000)),
    ]


class TestReadmeDrvs(unittest.TestCase):
    def test_readme_drv_list_covered(self):
        """Matrix must include every bullet from README Supported DRVs."""
        readme = (Path(__file__).parent / "README.md").read_text()
        listed = []
        for line in readme.splitlines():
            if line.startswith("* DRV") or line.startswith("* EC_ESC_Driver"):
                name = line[2:].split("(")[0].split("—")[0].strip()
                listed.append(name)
        matrix_names = {e["drv"] for e in DRV_MATRIX}
        missing = [n for n in listed if n not in matrix_names]
        self.assertEqual(missing, [], f"README DRVs missing from DRV_MATRIX: {missing}")

    def test_each_drv_smoke(self):
        from mi_patcher import MiPatcher

        for entry in DRV_MATRIX:
            drv = entry["drv"]
            with self.subTest(drv=drv):
                path = _resolve(entry)
                if path is None:
                    self.skipTest(f"{drv}: no plaintext ESC bin found")
                stock = path.read_bytes()
                ok = 0
                errors = []
                for mod, _ in _core_mods(MiPatcher(bytearray(stock), entry["model"])):
                    p = MiPatcher(bytearray(stock), entry["model"])
                    try:
                        ret = dict(_core_mods(p))[mod]()
                        _assert_sites(p.data, ret, stock, mod)
                        ok += 1
                    except Exception as e:
                        errors.append(f"{mod}:{type(e).__name__}")
                self.assertGreaterEqual(
                    ok,
                    entry["min_ok"],
                    f"{drv} ({path.name}): only {ok} mods ok, need >={entry['min_ok']}; "
                    f"fails={errors}",
                )


class TestXiaomiOtaMcu(unittest.TestCase):
    """firmware/ota/xiaomi MCU images — not classic MiPatcher ESC payloads."""

    def test_inventory_mcu_bins(self):
        if not XIAOMI.is_dir():
            self.skipTest("firmware/ota/xiaomi missing")
        mcus = sorted(
            {
                p.resolve()
                for p in XIAOMI.rglob("*_mcu_*.bin")
                if p.is_file() and p.stat().st_size < 2_000_000
            }
        )
        self.assertGreater(len(mcus), 0, "expected Xiaomi MCU OTA bins")

        products = set()
        no_esc_header = 0
        for p in mcus:
            data = p.read_bytes()
            if b"Scooter_Mi" not in data[:0x2000] and b"Scooter_Mi" not in data:
                no_esc_header += 1
            if "mcu_xiaomi.scooter." in p.name:
                products.add(p.name.split("mcu_xiaomi.scooter.")[-1].removesuffix(".bin"))

        # These are full MCU images / signed blobs, not EC_ESC_Driver cuts.
        self.assertEqual(
            no_esc_header,
            len(mcus),
            "unexpected Scooter_Mi* header inside Xiaomi MCU OTAs "
            "(would need MiPatcher mapping)",
        )
        self.assertGreaterEqual(len(products), 5)
        # Keep a stable note of what we have for future porting.
        print(f"\nXiaomi MCU products ({len(products)}): {sorted(products)}")
        print(f"MCU bin files scanned: {len(mcus)}")


# --- V1.0.1.5 (4proita) offset oracles ---

# File offsets (VA = 0x08004000 + off) — test oracles only
OFF_V1015 = {
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

MSS_SCALE_V1015 = 410
_KS = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_THUMB)


def _asm(s: str) -> bytes:
    return bytes(_KS.asm(s)[0])


def _make_v1015_patcher(data: bytes):
    from mi_patcher import MiPatcher
    return MiPatcher(bytearray(data), "4proita")


def _load_fw(path: Path) -> bytes:
    if not path.is_file():
        raise unittest.SkipTest(f"missing firmware: {path}")
    return path.read_bytes()


class TestV1015Patches(unittest.TestCase):
    """V1.0.1.5 (STM32F4) patch oracles for MiPatcher(..., \"4proita\")."""

    @classmethod
    def setUpClass(cls):
        cls.stock = _load_fw(F4_BIN)

    def setUp(self):
        self.p = _make_v1015_patcher(self.stock)

    def test_speed_limits(self):
        r = self.p.speed_limit_ped(9)
        _assert_sites(self.p.data, r, self.stock, "speed_limit_ped")
        self.assertEqual(
            self.p.data[OFF_V1015["speed_ped"]:OFF_V1015["speed_ped"] + 4],
            _asm("MOV.W R9, #9"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.speed_limit_drive(22)
        _assert_sites(self.p.data, r, self.stock, "speed_limit_drive")
        self.assertEqual(
            self.p.data[OFF_V1015["speed_drive"]:OFF_V1015["speed_drive"] + 2],
            _asm("MOVS R0, #22"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.speed_limit_sport(27)
        _assert_sites(self.p.data, r, self.stock, "speed_limit_sport")
        self.assertEqual(
            self.p.data[OFF_V1015["speed_sport"]:OFF_V1015["speed_sport"] + 2],
            _asm("MOVS R3, #27"),
        )

    def test_crc(self):
        r = self.p.current_raising_coeff(600)
        _assert_sites(self.p.data, r, self.stock, "current_raising_coeff")
        self.assertEqual(
            self.p.data[OFF_V1015["crc"]:OFF_V1015["crc"] + 4],
            _asm("MOVW R2, #600"),
        )

    def test_amperes(self):
        r = self.p.ampere_ped(10000)
        _assert_sites(self.p.data, r, self.stock, "ampere_ped")

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.ampere_drive(20000)
        _assert_sites(self.p.data, r, self.stock, "ampere_drive")
        self.assertEqual(
            self.p.data[OFF_V1015["amp_drive_cmp"]:OFF_V1015["amp_drive_cmp"] + 2],
            _asm("CMP R0, R0"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.ampere_sport(30000)
        _assert_sites(self.p.data, r, self.stock, "ampere_sport")
        self.assertEqual(
            self.p.data[OFF_V1015["amp_sport_cmp"]:OFF_V1015["amp_sport_cmp"] + 2],
            _asm("CMP R0, R0"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.ampere_max(10000, 35000, 55000)
        _assert_sites(self.p.data, r, self.stock, "ampere_max")

    def test_kers_and_autobrake(self):
        r = self.p.remove_kers()
        _assert_sites(self.p.data, r, self.stock, "remove_kers")
        self.assertEqual(
            self.p.data[OFF_V1015["kers"]:OFF_V1015["kers"] + 2],
            _asm("MOVS R0, #0"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.kers_multi(2, 5, 10)
        _assert_sites(self.p.data, r, self.stock, "kers_multi")
        self.assertEqual(len(bytes.fromhex(r[0][3])), 32)

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.remove_autobrake()
        _assert_sites(self.p.data, r, self.stock, "remove_autobrake")
        self.assertEqual(
            self.p.data[OFF_V1015["autobrake"]:OFF_V1015["autobrake"] + 4],
            _asm("MOVW R12, #0xffff"),
        )

    def test_motor_start(self):
        r = self.p.motor_start_speed(3.0)
        _assert_sites(self.p.data, r, self.stock, "motor_start_speed")
        self.assertEqual(int(r[0][1], 16), OFF_V1015["mss_hi"])
        self.assertEqual(
            bytes.fromhex(r[0][3]),
            _asm(f"MOVW R7, #{int(round(3.0 * MSS_SCALE_V1015))}"),
        )

    def test_charge_dpc_cc_shutdown(self):
        r = self.p.remove_charging_mode()
        _assert_sites(self.p.data, r, self.stock, "remove_charging_mode")
        self.assertEqual(
            self.p.data[OFF_V1015["charge_cbz"]:OFF_V1015["charge_cbz"] + 2],
            _asm("NOP"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.dpc()
        _assert_sites(self.p.data, r, self.stock, "dpc")
        self.assertEqual(
            self.p.data[OFF_V1015["dpc_clear"]:OFF_V1015["dpc_clear"] + 4],
            _asm("NOP") * 2,
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.cc_delay(2.0)
        _assert_sites(self.p.data, r, self.stock, "cc_delay")
        self.assertEqual(
            self.p.data[OFF_V1015["cc_delay"]:OFF_V1015["cc_delay"] + 4],
            _asm("MOV.W R1, #400"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.shutdown_time(1.0)
        _assert_sites(self.p.data, r, self.stock, "shutdown_time")
        self.assertEqual(
            self.p.data[OFF_V1015["shutdown"]:OFF_V1015["shutdown"] + 4],
            _asm("CMP.W R0, #200"),
        )

    def test_region_modellock_volt_lights(self):
        r = self.p.region_free()
        _assert_sites(self.p.data, r, self.stock, "region_free")
        self.assertEqual(
            self.p.data[OFF_V1015["region_3e"]:OFF_V1015["region_3e"] + 4],
            _asm("NOP.W"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.remove_modellock()
        _assert_sites(self.p.data, r, self.stock, "remove_modellock")
        self.assertEqual(
            self.p.data[OFF_V1015["modellock"]:OFF_V1015["modellock"] + 2],
            b"\x01\xe0",
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.volt_limit(45.01)
        _assert_sites(self.p.data, r, self.stock, "volt_limit")
        self.assertNotEqual(r[0][2], r[0][3])

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.ped_noblink()
        _assert_sites(self.p.data, r, self.stock, "ped_noblink")
        self.assertEqual(
            self.p.data[OFF_V1015["ped_beq"]:OFF_V1015["ped_beq"] + 2],
            _asm("NOP"),
        )

        self.p = _make_v1015_patcher(self.stock)
        r = self.p.brake_light_static()
        _assert_sites(self.p.data, r, self.stock, "brake_light_static")
        self.assertEqual(
            self.p.data[OFF_V1015["blm_brake"]:OFF_V1015["blm_brake"] + 2],
            _asm("CMP R1, #0xFF"),
        )
        self.assertEqual(
            self.p.data[OFF_V1015["blm_ped"]:OFF_V1015["blm_ped"] + 2],
            _asm("CMP R1, #0xFF"),
        )

    def test_f1_regression_speed_drive(self):
        stock = _load_fw(F1_BIN)
        from mi_patcher import MiPatcher
        p = MiPatcher(bytearray(stock), "4pro")
        r = p.speed_limit_drive(22)
        self.assertTrue(r)
        ofs = int(r[0][1], 16)
        post = bytes.fromhex(r[0][3])
        self.assertEqual(p.data[ofs:ofs + len(post)], post)
        self.assertNotEqual(r[0][2], r[0][3])


if __name__ == "__main__":
    unittest.main(verbosity=2)
