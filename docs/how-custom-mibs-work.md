```markdown
# SR Linux Custom SNMP MIBs

A community collection of **custom SNMP MIBs** for Nokia SR Linux using the official gNMI-to-SNMP framework (introduced in 24.10.1+).

Turn any gNMI path (fan speed, temperature, optics, QoS, etc.) into a standard SNMP table that works with Zabbix, LibreNMS, Prometheus, etc.

## Features

- Zero external dependencies (pure Python + Nokia `utilities` module)
- Works on real hardware **and** Containerlab
- Includes a simple generator so you can add new MIBs in < 30 seconds
- Fully tested on 7250 IXR-X1B (v25.7)

## Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/YOURUSERNAME/srl-custom-snmp-mibs.git
   cd srl-custom-snmp-mibs
   ```

2. Copy the MIB you want to your SR Linux router:
   ```bash
   scp -r mibs/control-temperature/* admin@your-router/opt/srlinux/snmp/scripts/
   ```

3. Add the YAML to the config:
   ```bash
   echo "  - scripts/nokiaControlTemperatureTable.yaml" >> /opt/srlinux/snmp/snmp_files_config.yaml
   ```

4. Restart SNMP:
   ```bash
   /tools system app-management application snmp_server-mgmt restart
   ```

5. Test it:
   ```bash
   snmpwalk -v2c -c <community> <router-ip> 1.3.6.1.4.1.6527.100.2.1
   ```

## Included MIBs

### 1. Control Card Temperature (`nokiaControlTemperatureTable`)

- **OID base**: `1.3.6.1.4.1.6527.100.2.1`
- **gNMI path**: `/platform/control[slot=*]/temperature`
- **Columns**: `controlSlot`, `temperatureInstant` (in °C)

### 2. Fan Tray Speed (`nokiaFanSpeedTable`)

- **OID base**: `1.3.6.1.4.1.6527.100.1.1`
- **gNMI path**: `/platform/fan-tray[id=*]`
- **Columns**: `fanTrayId`, `fanSpeed` (returns 0 in lab, real value on hardware)

## Adding Your Own MIB (Super Simple)

Use the included generator:

```bash
cd tools
cp example-mibs.csv my-mibs.csv
# edit my-mibs.csv with your new table
python3 generate_custom_mib.py my-mibs.csv
```

Then copy the generated files into `mibs/your-new-mib/` and follow the Quick Start.

## Prerequisites

- SR Linux 24.10.1 or newer
- SNMP server enabled (`system snmp`)
- Read access to the desired gNMI paths

## License

MIT License — feel free to use, modify, and contribute!

## Contributing

PRs welcome! Just open an issue or PR with your new MIB.

---
Made with ❤️ for the SR Linux community.
```

---

### 3. Next Steps (I’ll do the heavy lifting)

Just tell me:

1. **Your GitHub username** (so I can suggest the exact repo URL)
2. Do you want me to also generate the **fan-speed** files in the same polished format as the temperature one?
3. Any other MIBs you want included in the first release? (optics, power supply, BGP peer count, etc.)

Once you confirm, I’ll give you:
- The exact `nokiaControlTemperatureTable.yaml` + `.py` files (final cleaned-up versions)
- The fan-speed pair
- The `example-mibs.csv` and generator script (already updated)

Then you can create the repo in 30 seconds and push everything.

Ready when you are — just say **“go”** (or give me your GitHub username) and we’ll launch this thing! 🚀