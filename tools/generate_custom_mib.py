#!/usr/bin/python3
import json
import sys
import os
import subprocess
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def load_mibs_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    with open(filename, 'r') as f:
        if ext in ('.yaml', '.yml'):
            if not HAS_YAML:
                print("❌ PyYAML required → sudo apt-get install python3-yaml")
                sys.exit(1)
            return yaml.safe_load(f)
        elif ext == '.json':
            return json.load(f)
        else:
            print("❌ Only .yaml/.yml or .json supported")
            sys.exit(1)

def run_sudo_command(cmd, description):
    print(f"   🔨 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"   📤 {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ FAILED: {e.stderr.strip() or e}")
        sys.exit(1)

def line_exists_in_config(pattern, config_file):
    result = subprocess.run(f'sudo grep -q "{pattern}" {config_file}', shell=True, capture_output=True)
    return result.returncode == 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_custom_mib.py <mibs.yaml>")
        sys.exit(1)

    input_file = sys.argv[1]
    scripts_dir = "/opt/srlinux/snmp/scripts"
    config_file = "/opt/srlinux/snmp/snmp_files_config.yaml"

    print("🚀 Starting Simplified Custom SNMP MIB Generator")
    print("="*80)

    mibs = load_mibs_file(input_file)

    for mib in mibs:
        table      = mib['table_name'].strip()
        oid_base   = mib['oid_base'].strip()
        path       = mib['path'].strip()
        top_key    = mib.get('top_level_key', '').strip()
        idx_field  = mib.get('index_field', '').strip()
        idx_name   = mib['index_name'].strip()
        idx_oid    = mib['index_oid'].strip()
        val_field  = mib.get('value_field', '').strip()
        col_name   = mib['column_name'].strip()
        col_oid    = mib['column_oid'].strip()
        col_syntax = mib['column_syntax'].strip()

        yaml_file = f"{table}.yaml"
        py_file   = f"{table}.py"

        print(f"📦 Processing → {table}")

        # Generate YAML
        yaml_content = f"""# Auto-generated custom MIB for {table}
paths:
  - {path}
python-script: {py_file}
enabled: true
debug: false
tables:
  - name:    {table}
    enabled: true
    oid:     {oid_base}
    indexes:
      - name:   {idx_name}
        oid:    {idx_oid}
        syntax: integer
    columns:
      - name:   {col_name}
        oid:    {col_oid}
        syntax: {col_syntax}
"""
        local_yaml = f"/tmp/{yaml_file}"
        with open(local_yaml, 'w') as y: y.write(yaml_content)

        run_sudo_command(f"sudo tee {scripts_dir}/{yaml_file} > /dev/null < {local_yaml}",
                        f"Installing {yaml_file}")

        # Generate Python (simplified value_field support)
        py_content = f'''#!/usr/bin/python
import sys
import json
from collections import OrderedDict
import utilities

def index_to_int(idx):
    if isinstance(idx, (int, float)): return int(idx)
    s = str(idx).strip().upper()
    if s.isdigit(): return int(s)
    if s and s[0].isalpha(): return ord(s[0]) - ord('A') + 1
    return 0

db: dict = {{}}

def store_value(store: dict, name: str, value) -> None:
    if value is not None: store[name] = value

def store_data(items: list) -> None:
    print(f"DEBUG: Received {{len(items or [])}} items")
    for item in items or []:
        idx = item.get('{idx_field}') or item.get('id') or item.get('slot')
        if idx is None: continue
        key = index_to_int(idx)

        value = item.get('{val_field}')
        if value is None and 'temperature' in item:
            value = item.get('temperature', {{}}).get('{val_field}')
        if value is None: value = 0

        print(f"DEBUG: index={{idx}} → key={{key}} → {col_name}={{value}}")
        obj: dict = {{}}
        store_value(obj, '{idx_name}', key)
        store_value(obj, '{col_name}', value)
        db[key] = obj

def gen_table() -> list:
    rows = []
    for k, v in db.items():
        row = {{}}
        objects = OrderedDict()
        store_value(objects, '{idx_name}', v.get('{idx_name}'))
        store_value(objects, '{col_name}', v.get('{col_name}'))
        row['objects'] = objects
        rows.append(row)
    print(f"DEBUG: Generated {{len(rows)}} rows")
    return rows

def snmp_main(in_json_str: str) -> str:
    global db
    db = {{}}
    in_json = json.loads(in_json_str)
    utilities.process_snmp_info(in_json.get('_snmp_info_'))
    platform = in_json.get('platform', {{}})
    data = platform.get('{top_key}', []) or in_json.get('{top_key}', [])
    store_data(data)
    response = {{'tables': {{}}}}
    if utilities.is_table_enabled('{table}'):
        response['tables']['{table}'] = gen_table()
    return json.dumps(response, separators=(',', ':'))
'''
        local_py = f"/tmp/{py_file}"
        with open(local_py, 'w') as p: p.write(py_content)

        run_sudo_command(f"sudo tee {scripts_dir}/{py_file} > /dev/null < {local_py}",
                        f"Installing {py_file}")

        if line_exists_in_config(f"scripts/{yaml_file}", config_file):
            print(f"   ℹ️  Already in table-definitions")
        else:
            run_sudo_command(f'sudo sed -i "/^table-definitions:/a\\  - scripts/{yaml_file}" {config_file}',
                            f"Adding {yaml_file} to table-definitions")

        os.unlink(local_yaml)
        os.unlink(local_py)
        print(f"   🧹 Cleaned /tmp")

        print("-" * 70)

    print("\n🎉 All MIBs installed successfully!")
    print("Run: /tools system app-management application snmp_server-mgmt restart")

if __name__ == "__main__":
    main()
