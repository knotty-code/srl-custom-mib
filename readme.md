```markdown
# SR Linux Custom SNMP MIBs

A community collection of **custom SNMP MIBs** for Nokia SR Linux using the official gNMI-to-SNMP framework (introduced in 24.10.1+).

Turn any gNMI path (fan speed, temperature, optics, MTU, QoS, etc.) into a standard SNMP table that works with Zabbix, LibreNMS, Prometheus, etc.

## Features

- Zero external dependencies (pure Python + Nokia `utilities` module)
- Works on real hardware **and** Containerlab
- Includes a simple generator so you can add new MIBs in < 30 seconds
- Fully tested on 7250 IXR-X1B (v25.7+)

## Quick Start

1. **On your laptop/workstation** – Clone the repository:
   ```bash
   git clone https://github.com/knotty-code/srl-custom-mib.git
   cd srl-custom-mib
   ```

2. Copy the tools and example files to your SR Linux router:
   ```bash
   scp -r tools/* <your-username>@<router-ip>:/tmp/
   ```

3. **On the SR Linux router** – Log in and grant yourself superuser rights:
   ```bash
   ssh <your-username>@<router-ip>
   configure
   set / system aaa authentication user <your-username> superuser true
   commit
   exit
   ```

4. Enter the Linux shell and run the generator:
   ```bash
   bash
   cd /tmp
   python3 generate_custom_mib.py mibs.yaml
   ```

5. Restart the SNMP server:
   ```bash
   tools system app-management application snmp_server-mgmt restart
   ```

6. Test the included MIBs:
   ```bash
   snmpwalk -v2c -c <community> <router-ip> 1.3.6.1.4.1.6527.100.2.1   # temperature
   snmpwalk -v2c -c <community> <router-ip> 1.3.6.1.4.1.6527.100.1.1   # fan speed
   snmpwalk -v2c -c <community> <router-ip> 1.3.6.1.4.1.6527.100.4.1   # optics output power
   snmpwalk -v2c -c <community> <router-ip> 1.3.6.1.4.1.6527.100.5.1   # interface MTU
   ```

## Understanding `mibs.yaml`

This file controls which MIBs get created. It is intentionally simple and well-commented.

### How to discover the correct values

Run this command on the router to see the exact JSON structure:

```bash
info from state / platform <container> * <leaf> detail | as json
```

**Examples:**
```bash
info from state / platform control * temperature | as json
info from state / platform fan-tray * | as json
info from state / interface * mtu | as json
```

### Field descriptions

| Field              | Description                                                                 | Example                     |
|--------------------|-----------------------------------------------------------------------------|-----------------------------|
| `table_name`       | SNMP table name (must be unique)                                            | `nokiaControlTemperatureTable` |
| `oid_base`         | Base OID for the table                                                      | `1.3.6.1.4.1.6527.100.2.1` |
| `path`             | Full gNMI path                                                              | `/platform/control[slot=*]/temperature` |
| `top_level_key`    | The main list name under "platform" in the JSON                             | `control`                   |
| `index_field`      | JSON key that identifies each row                                           | `slot` or `name`            |
| `index_name`       | Friendly name for the index column                                          | `controlSlot`               |
| `index_oid`        | OID for the index column                                                    | `1.3.6.1.4.1.6527.100.2.1.1` |
| `value_field`      | The leaf you want (no dotted notation needed)                               | `instant` or `speed`        |
| `column_name`      | Friendly name for the value column                                          | `temperatureInstant`        |
| `column_oid`       | OID for the value column                                                    | `1.3.6.1.4.1.6527.100.2.1.2` |
| `column_syntax`    | SNMP data type                                                              | `integer32`, `gauge32`      |
| `description`      | Human readable comment                                                      | `Control card CPU temperature in Celsius` |

### Included MIBs

- **Control Card Temperature** (`nokiaControlTemperatureTable`)
- **Fan Tray Speed** (`nokiaFanSpeedTable`)
- **Transceiver Output Power** (channel 1) (`nokiaOpticsOutputPowerTable`)
- **Interface MTU** (`nokiaInterfaceMtuTable`)

## Adding Your Own MIB

1. Run the discovery command above to see the JSON structure.
2. Copy one of the example blocks in `mibs.yaml` and update the fields.
3. Re-run the generator:
   ```bash
   python3 /tmp/generate_custom_mib.py /tmp/mibs.yaml
   ```
4. Restart SNMP:
   ```bash
   tools system app-management application snmp_server-mgmt restart
   ```

Made with ❤️ for the SR Linux community.
```