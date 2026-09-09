# NextGen firmware patcher
Little firmware modifications to make your day  nicer.

This patcher is based on BotoX' [m365 firmware patcher](https://github.com/BotoX/xiaomi-m365-firmware-patcher).

New mods / contributions highly welcome, simply open PR and present your mod!
The mod will then be integrated into the NGFW patcher.

## Supported DRVs
* DRV016
* DRV017
* DRV242
* DRV245
* DRV247
* DRV248
* DRV252
* DRV319
* DRV321
* DRV022 (Experimental)
* DRV0037 (Experimental)
* DRV176 (Experimental)
* DRV1415 (Experimental)
* EC_ESC_Driver_V1.0.1.5 (Experimental) — `mi_patcher.py` (`4proita`)

## Available Mods
* DPC (register)
* No Charging Fix
* Remove Speed Check
* Motor Start Speed
* Cruise Control Delay
* Current Raising Coefficient
* Wheelsize
* Speed Limits
* Phase Currents
* Brake Currents
* Shutdown Time
* No KERS (improved)
* Current Meter
* Region Free
* Brakelight + Auto-Light
* Pedestrian -> ECO Mode
* Pedestrian No-Blink
* Button Swap
* Remove Model Lock
* Custom KERS

### EC_ESC_Driver_V1.0.1.5 (`mi_patcher.py` / `4proita`)

FindPattern / `SignatureException` ladders for `Scooter_Mi4PRO_ST_F400_V15` (same style as other DRVs). CLI:

```bash
python3 cli.py mi 4proita EC_ESC_Driver_V1.0.1.5.bin out.bin sld,sls,slp,rcm,rfm,rml,mss,sdt,vlt,pnb,dpc,ccd,rab,rks,kml
```

Ported: speed limits, phase/max amps, CRC, KERS / kers_multi, autobrake, motor start, charge gate, DPC, CC delay, shutdown, region free, modellock, volt limit, ped_noblink, static brakelight.  
Not yet: wheel const, ampere_brake, ampere_meter, BMS baud, auto-light, button swap.

Tests: `python3 -m unittest test_v1015 test_drvs`

### Your Mods??
Contribute your mod to this project!

## Instructions
1. `FLASK_APP=app/__init__.py`
2. `flask run` to start the flask app

## License
Licensed under AGPLv3, see [LICENSE.md](LICENSE.md).
