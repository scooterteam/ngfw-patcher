// Device presets and form handling logic
const forms = {
    "VERSION": "version",
    "DPC": "dpc",
    "MOTOR_START_SPEED": "motor_start_speed",
    "REMOVE_KERS": "remove_kers",
    "REMOVE_AUTOBRAKE": "remove_autobrake",
    "REMOVE_CHARGING_MODE": "remove_charging_mode",
    "CC_DELAY": "cc_delay",
    "CRC": "crc",
    "WHEELSIZE": "wheelsize",
    "SHUTDOWN_TIME": "shutdown_time",
    "SL": "sl_cb",
    "SL_SPORT": "sl_sport",
    "SL_DRIVE": "sl_drive",
    "SL_PED": "sl_ped",
    "AMPS": "amps_cb",
    "AMPS_SPORT": "amps_sport",
    "AMPS_DRIVE": "amps_drive",
    "AMPS_PED": "amps_ped",
    "AMPS_MAX": "amps_max_cb",
    "AMPS_SPORT_MAX": "amps_sport_max",
    "AMPS_DRIVE_MAX": "amps_drive_max",
    "AMPS_PED_MAX": "amps_ped_max",
    "AMPS_BRAKE_MIN": "amps_brake_min",
    "AMPS_BRAKE_MAX": "amps_brake_max",
    "AMMETER": "ammeter",
    "RFM": "rfm",
    "RML": "rml",
    "DMN": "dmn",
    "EMBED_ENC_KEY": "embed_enc_key",
    "CUSTOM_ENC_KEY": "custom_enc_key",
    "EMBED_RAND_CODE": "embed_rand_code",
    "US_REGION_SPOOF": "us_region_spoof",
    "ALLOW_SN_CHANGE": "allow_sn_change",
    "BLM": "blm",
    "BLM_ALM": "blm_alm",
    "BAUD": "baud",
    "VOLT": "volt",
    "ECO_MODE": "eco_mode",
    "PNB": "pnb",
    "BTS": "bts",
    "KML": "kml",
    "KML_L0": "kml_l0",
    "KML_L1": "kml_l1",
    "KML_L2": "kml_l2",
};

// Move all functions from the script section
function OnSliderChange(elname, value) {
    const ws_val = document.getElementById(elname);
    ws_val.innerHTML = value;
}

function Round(value) {
    return Math.round(value * 10) / 10;
}

function SliderUp(name, valuename) {
    const slider = document.getElementsByName(name)[0];
    if (slider.disabled) {
        return;
    }
    const value = Round(parseFloat(slider.value) + parseFloat(slider.step));
    slider.value = value;
    OnSliderChange(valuename, value);
}

function SliderDown(name, valuename) {
    const slider = document.getElementsByName(name)[0];
    if (slider.disabled) {
        return;
    }
    const value = Round(parseFloat(slider.value) - parseFloat(slider.step));
    slider.value = value;
    OnSliderChange(valuename, value);
}

function GetForm(name) {
    return document.getElementsByName(name)[0];
}

function GetFormValue(name) {
    const o = GetForm(name);
    if (o.type === "checkbox") {
        return o.checked;
    }
    return o.value;
}

function GetPatchCheckBox(name) {
    return GetForm(`${name}_cb`);
}

function CheckForm(name, cb) {
    const o = GetForm(name);
    if (o.value != 0) {
        // temp
        const dev = document.getElementById("devselect").value;
        if (dev == '4pro' && name == forms.BLM_ALM) {
            return;
        }
        o.disabled = !cb.checked;

        // Update parent card styling if this is a checkbox
        if (cb.type === 'checkbox') {
            const card = cb.closest('.card');
            if (card) {
                card.classList.toggle('checked', cb.checked);
            }
        }
    }
}

function ChangeForm(name, value, patch) {
    const o = GetForm(name);
    if (o.type === "checkbox") {
        o.checked = value;
        // Update card styling
        const card = o.closest('.card');
        if (card) {
            card.classList.toggle('checked', value);
        }
    } else {
        o.value = value;
    }
    if (o.onchange) { o.onchange(); }

    if (typeof patch === 'boolean') {
        const cb = GetPatchCheckBox(name);
        if (cb) {
            cb.checked = patch;
            if (cb.onchange) { cb.onchange(); }
            // Update card styling for patch checkbox
            const card = cb.closest('.card');
            if (card) {
                card.classList.toggle('checked', patch);
            }
        }
    }
}

function OnLoad() {
    const warning = new bootstrap.Modal(document.getElementById('disclaimer'));
    warning.show();
    ChangeDevice();
}

function UdateVisibilityForDevice(dev) {
    const dkcElTitleNinebot = document.querySelector("#disable_key_check .form-check-label:nth-last-of-type(1)");
    const dkcElTitleXiaomi = document.querySelector("#disable_key_check .form-check-label:nth-last-of-type(2)");
    const dkcElInfoNinebot = document.querySelector("#disable_key_check .card-body:nth-last-of-type(1)");
    const dkcElInfoXiaomi = document.querySelector("#disable_key_check .card-body:nth-last-of-type(2)");

    switch (dev) {
        case "pro2":
        case "1s":
        case "lite":
        case "mi3":
        case "4pro":
        case "4plus":
        case "4max":
            dkcElTitleNinebot.style.display = 'none';
            dkcElTitleXiaomi.style.display = 'inline';
            dkcElInfoNinebot.style.display = 'none';
            dkcElInfoXiaomi.style.display = 'block';
            break;
        case "f2pro":
        case "f2plus":
        case "f2":
        case "g2":
        case "zt3pro":
        case "g3":
            dkcElTitleNinebot.style.display = 'inline';
            dkcElTitleXiaomi.style.display = 'none';
            dkcElInfoNinebot.style.display = 'block';
            dkcElInfoXiaomi.style.display = 'none';
            break;
        default:
            throw new Error('Unexpected device');
    }
}

function ChangeDevice() {
    Preset_Default();
    const dev = document.getElementById("devselect").value;
    UdateVisibilityForDevice(dev);

    switch (dev) {
        case "pro2": Preset_Pro2(); break;
        case "1s": Preset_1S(); break;
        case "lite": Preset_Lite(); break;
        case "mi3": Preset_Mi3(); break;
        case "4pro": Preset_4Pro(); break;
        case "4plus": Preset_4ProPlus(); break;
        case "4max": Preset_4ProMax(); break;
        case "f2pro": Preset_F2Pro(); break;
        case "f2plus": Preset_F2Plus(); break;
        case "f2": Preset_F2(); break;
        case "g2": Preset_G2(); break;
        case "zt3pro": Preset_ZT3Pro(); break;
        case "g3": Preset_G3(); break;
    }
}

function Preset_1S() {
    ChangeForm(forms.AMPS_SPORT, "20000", false);
    ChangeForm(forms.AMPS_DRIVE, "15000", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "35000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "28000", false);
    ChangeForm(forms.AMPS_BRAKE_MAX, "52000", false);
    GetForm(forms.DMN).disabled = true;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = true;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = true;
}

function Preset_Pro2() {
    ChangeForm(forms.AMPS_SPORT, "25000", false);
    ChangeForm(forms.AMPS_DRIVE, "17000", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "55000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "32000", false);
    ChangeForm(forms.AMPS_BRAKE_MAX, "52000", false);
    GetForm(forms.DMN).disabled = true;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = true;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = true;
}

function Preset_Lite() {
    ChangeForm(forms.SL_SPORT, "20", false);
    ChangeForm(forms.SL_DRIVE, "15", false);
    ChangeForm(forms.AMPS_SPORT, "17000", false);
    ChangeForm(forms.AMPS_DRIVE, "0", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "32000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "0", false);
    ChangeForm(forms.AMPS_BRAKE_MAX, "22000", false);
    GetForm(forms.RFM).disabled = true;
    GetForm(forms.DMN).disabled = true;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = true;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = true;
}

function Preset_Mi3() {
    ChangeForm(forms.AMPS_SPORT, "26500", false);
    ChangeForm(forms.AMPS_DRIVE, "15000", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "55000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "28000", false);
    ChangeForm(forms.AMPS_BRAKE_MAX, "47000", false);
    GetForm(forms.DMN).disabled = true;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = true;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = true;
}

function Preset_4Pro() {
    ChangeForm(forms.AMPS_SPORT, "26500", false);
    ChangeForm(forms.AMPS_DRIVE, "19000", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "55000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "35000", false);
    ChangeForm(forms.AMPS_BRAKE_MAX, "57000", false);
    ChangeForm(forms.WHEELSIZE, "10.0", false);
    GetForm(forms.DMN).disabled = true;
    GetForm(forms.RML).disabled = true;
    GetForm(forms.BTS).disabled = true;
    GetForm(forms.BLM_ALM).disabled = true;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = true;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = true;
}

function Preset_4ProPlus() {
    Preset_4ProMax();
}

function Preset_4ProMax() {
    DisableAll(true);
    ChangeForm(forms.VOLT, "60.01", false);
    GetForm(forms.CC_DELAY + "_cb").disabled = false;
    GetForm(forms.RFM).disabled = false;
    GetForm(forms.SL).disabled = false;
    GetForm(forms.REMOVE_AUTOBRAKE).disabled = false;
    GetForm(forms.REMOVE_CHARGING_MODE).disabled = false;
    GetForm(forms.VOLT + "_cb").disabled = false;
    GetForm(forms.CUSTOM_ENC_KEY + "_cb").disabled = false;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = true;
}

function Preset_F2Pro() {
    Preset_F2Base();
    ChangeForm(forms.AMPS_DRIVE, "20000", false);
    ChangeForm(forms.AMPS_SPORT, "28000", false);
}

function Preset_F2Plus() {
    Preset_F2Base();
    ChangeForm(forms.AMPS_SPORT, "26000", false);
}

function Preset_F2() {
    Preset_F2Base();
    ChangeForm(forms.AMPS_SPORT, "24000", false);
}

function Preset_F2Base() {
    ChangeForm(forms.SL_SPORT, "25", false);
    ChangeForm(forms.SL_DRIVE, "20", false);
    ChangeForm(forms.SL_PED, "15", false);
    ChangeForm(forms.AMPS_PED, "9000", false);
    ChangeForm(forms.AMPS_DRIVE, "18000", false);
    ChangeForm(forms.AMPS_PED_MAX, "30000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "40000", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "72000", false);
    ChangeForm(forms.WHEELSIZE, "10.0", false);
    ChangeForm(forms.VOLT, "45.01", false);

    GetForm(forms.BTS).disabled = true;
    GetForm(forms.BLM).disabled = true;
    GetForm(forms.MOTOR_START_SPEED + "_cb").disabled = true;
    GetForm(forms.CRC + "_cb").disabled = true;
    GetForm(forms.WHEELSIZE + "_cb").disabled = true;
    GetForm(forms.SHUTDOWN_TIME + "_cb").disabled = true;
    GetForm(forms.AMPS_BRAKE_MIN + "_cb").disabled = true;
    GetForm(forms.AMPS_BRAKE_MAX + "_cb").disabled = true;
    GetForm(forms.AMMETER).disabled = true;
    GetForm(forms.ECO_MODE).disabled = true;
    GetForm(forms.PNB).disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
}

function Preset_G2() {
    ChangeForm(forms.SL_SPORT, "25", false);
    ChangeForm(forms.SL_DRIVE, "20", false);
    ChangeForm(forms.SL_PED, "15", false);
    ChangeForm(forms.AMPS_PED, "8000", false);
    ChangeForm(forms.AMPS_DRIVE, "17000", false);
    ChangeForm(forms.AMPS_SPORT, "32340", false);
    ChangeForm(forms.AMPS_PED_MAX, "35000", false);
    ChangeForm(forms.AMPS_DRIVE_MAX, "55000", false);
    ChangeForm(forms.AMPS_SPORT_MAX, "80000", false);
    ChangeForm(forms.WHEELSIZE, "10.0", false);
    ChangeForm(forms.VOLT, "45.01", false);

    GetForm(forms.BTS).disabled = true;
    GetForm(forms.BLM).disabled = true;
    GetForm(forms.MOTOR_START_SPEED + "_cb").disabled = true;
    GetForm(forms.CRC + "_cb").disabled = true;
    GetForm(forms.CC_DELAY + "_cb").disabled = true;
    GetForm(forms.KML).disabled = true;
    GetForm(forms.WHEELSIZE + "_cb").disabled = true;
    GetForm(forms.SHUTDOWN_TIME + "_cb").disabled = true;
    GetForm(forms.AMPS_BRAKE_MIN + "_cb").disabled = true;
    GetForm(forms.AMPS_BRAKE_MAX + "_cb").disabled = true;
    GetForm(forms.AMMETER).disabled = true;
    GetForm(forms.BAUD).disabled = true;
    GetForm(forms.ECO_MODE).disabled = true;
    GetForm(forms.PNB).disabled = true;
    GetForm(forms.US_REGION_SPOOF).disabled = true;
}

function Preset_ZT3Pro() {
    DisableAll(true);
    GetForm(forms.RML).disabled = false;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = false;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = false;
    GetForm(forms.CUSTOM_ENC_KEY + "_cb").disabled = false;
    GetForm(forms.RFM).disabled = false;
    GetForm(forms.US_REGION_SPOOF).disabled = false;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = false;
}

function Preset_G3() {
    DisableAll(true);
    GetForm(forms.RML).disabled = false;
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = false;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = false;
    GetForm(forms.CUSTOM_ENC_KEY + "_cb").disabled = false;
    GetForm(forms.US_REGION_SPOOF).disabled = false;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = false;
}

function DisableAll(disable) {
    GetForm(forms.EMBED_ENC_KEY + "_cb").disabled = disable;
    GetForm(forms.CUSTOM_ENC_KEY + "_cb").disabled = disable;
    GetForm(forms.EMBED_RAND_CODE + "_cb").disabled = disable;
    GetForm(forms.DMN).disabled = disable;
    GetForm(forms.RML).disabled = disable;
    GetForm(forms.RFM).disabled = disable;
    GetForm(forms.BTS).disabled = disable;
    GetForm(forms.BLM).disabled = disable;
    GetForm(forms.DPC).disabled = disable;
    GetForm(forms.SL).disabled = disable;
    GetForm(forms.MOTOR_START_SPEED + "_cb").disabled = disable;
    GetForm(forms.REMOVE_AUTOBRAKE).disabled = disable;
    GetForm(forms.REMOVE_CHARGING_MODE).disabled = disable;
    GetForm(forms.REMOVE_KERS).disabled = disable;
    GetForm(forms.CC_DELAY + "_cb").disabled = disable;
    GetForm(forms.CRC + "_cb").disabled = disable;
    GetForm(forms.WHEELSIZE + "_cb").disabled = disable;
    GetForm(forms.SHUTDOWN_TIME + "_cb").disabled = disable;
    GetForm(forms.AMPS).disabled = disable;
    GetForm(forms.AMPS_MAX).disabled = disable;
    GetForm(forms.AMPS_BRAKE_MIN + "_cb").disabled = disable;
    GetForm(forms.AMPS_BRAKE_MAX + "_cb").disabled = disable;
    GetForm(forms.AMMETER).disabled = disable;
    GetForm(forms.VOLT + "_cb").disabled = disable;
    GetForm(forms.BAUD).disabled = disable;
    GetForm(forms.ECO_MODE).disabled = disable;
    GetForm(forms.PNB).disabled = disable;
    GetForm(forms.KML).disabled = disable;
    GetForm(forms.US_REGION_SPOOF).disabled = disable;
    GetForm(forms.ALLOW_SN_CHANGE).disabled = disable;
}

function Ped_To_Eco(cb) {
    if (!GetFormValue(forms.SL)) {
        CheckForm(forms.SL_PED, cb);
    }
    if (!GetFormValue(forms.AMPS)) {
        CheckForm(forms.AMPS_PED, cb);
    }
    if (!GetFormValue(forms.AMPS_MAX)) {
        CheckForm(forms.AMPS_PED_MAX, cb);
    }
    ChangeForm(forms.PNB, cb.checked);
    if (cb.checked) {
        ChangeForm(forms.SL_PED, "15", false);
        ChangeForm(forms.AMPS_PED, "13000", false);
        ChangeForm(forms.AMPS_PED_MAX, "26000", false);
    }
}

function Preset_Default() {
    DisableAll(false);

    ChangeForm(forms.DPC, false);
    ChangeForm(forms.MOTOR_START_SPEED, "5.0", false);
    ChangeForm(forms.REMOVE_AUTOBRAKE, false);
    ChangeForm(forms.REMOVE_KERS, false);
    ChangeForm(forms.REMOVE_CHARGING_MODE, false);
    ChangeForm(forms.CC_DELAY, "5", false);
    ChangeForm(forms.CRC, "300", false);
    ChangeForm(forms.WHEELSIZE, "8.5", false);
    ChangeForm(forms.SHUTDOWN_TIME, "3.0", false);
    ChangeForm(forms.SL, false);
    ChangeForm(forms.SL_SPORT, "25", false);
    ChangeForm(forms.SL_DRIVE, "20", false);
    ChangeForm(forms.SL_PED, "5", false);
    ChangeForm(forms.AMPS, false);
    ChangeForm(forms.AMPS_MAX, false);
    ChangeForm(forms.AMPS_PED, "7000", false);
    ChangeForm(forms.AMPS_PED_MAX, "8000", false);
    ChangeForm(forms.AMPS_BRAKE_MIN, "8000", false);

    ChangeForm(forms.AMMETER, false);
    ChangeForm(forms.RFM, false);
    ChangeForm(forms.RML, false);
    ChangeForm(forms.EMBED_ENC_KEY, "FE 80 1C B2 D1 EF 41 A6 A4 17 31 F5 A0 68 24 F0", false);
    ChangeForm(forms.CUSTOM_ENC_KEY, "FE 80 1C B2 D1 EF 41 A6 A4 17 31 F5 A0 68 24 F0", false);
    ChangeForm(forms.EMBED_RAND_CODE, "cfw.sh", false);
    ChangeForm(forms.US_REGION_SPOOF, false);
    ChangeForm(forms.ALLOW_SN_CHANGE, false);
    ChangeForm(forms.BLM, false);
    ChangeForm(forms.BLM_ALM, false);

    ChangeForm(forms.BAUD, false);
    ChangeForm(forms.VOLT, "43.01", false);

    ChangeForm(forms.ECO_MODE, false);
    ChangeForm(forms.PNB, false);
    ChangeForm(forms.BTS, false);

    ChangeForm(forms.KML, false);
    ChangeForm(forms.KML_L0, "6", null);
    ChangeForm(forms.KML_L1, "12", null);
    ChangeForm(forms.KML_L2, "20", null);
}

// Initialize form values from URL parameters on page load
const formValues = Object.values(forms);
const queryStrings = window.location.search.substring(1);
const queries = queryStrings.split('&');

for (const query of queries) {
    const [name, value] = query.split('=');
    if (formValues.includes(name)) {
        ChangeForm(name, value === 'on' ? true : value, true);
    }
}

// Replace the existing DOMContentLoaded event listener with this updated version
document.addEventListener('DOMContentLoaded', function () {
    // Add click handlers to all card headers
    document.querySelectorAll('.card-header').forEach(header => {
        // Find the checkbox in this card
        const checkbox = header.querySelector('input[type="checkbox"]');
        if (!checkbox) return;

        // Add click handler to the card header
        header.addEventListener('click', (e) => {
            // Don't toggle if clicking the checkbox directly or if the checkbox is disabled
            if (e.target === checkbox || checkbox.disabled) return;

            // Don't toggle if clicking on another input within the header
            if (e.target.tagName === 'INPUT') return;

            // Toggle the checkbox
            checkbox.checked = !checkbox.checked;

            // Trigger the change event for the checkbox
            checkbox.dispatchEvent(new Event('change'));

            // Toggle the checked class on the parent card
            header.closest('.card').classList.toggle('checked', checkbox.checked);
        });

        // Add change handler to checkbox to keep card styling in sync
        checkbox.addEventListener('change', () => {
            header.closest('.card').classList.toggle('checked', checkbox.checked);
        });

        // Set initial state
        header.closest('.card').classList.toggle('checked', checkbox.checked);
    });

    // Add collapse event handlers
    document.querySelectorAll('.section-header').forEach(header => {
        header.addEventListener('click', function () {
            // Toggle the chevron rotation
            const chevron = this.querySelector('.section-chevron');
            chevron.style.transform = this.getAttribute('aria-expanded') === 'true'
                ? 'rotate(180deg)'
                : 'rotate(0deg)';
        });
    });

    // Store collapse states in localStorage
    document.querySelectorAll('.collapse').forEach(collapse => {
        collapse.addEventListener('show.bs.collapse', function () {
            localStorage.setItem(this.id, 'expanded');
        });

        collapse.addEventListener('hide.bs.collapse', function () {
            localStorage.setItem(this.id, 'collapsed');
        });

        // Restore collapse state
        const state = localStorage.getItem(this.id);
        if (state === 'expanded') {
            new bootstrap.Collapse(collapse, { show: true });
        }
    });
});