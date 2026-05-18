#!/usr/bin/python
import sys
import json
from collections import OrderedDict
import utilities

db: dict = {}

def store_value(store: dict, name: str, value) -> None:
    if value is not None:
        store[name] = value

def store_data(items: list) -> None:
    for item in items or []:
        idx = item.get('controlslot') or item.get('id') or item.get('slot')
        if idx is None:
            continue
        value = item.get('temperatureinstant')
        if value is None and 'temperature' in item:
            value = item.get('temperature', {}).get('temperatureinstant')
        if value is None:
            value = 0
        key = int(idx) if str(idx).isdigit() else idx
        obj: dict = {}
        store_value(obj, 'controlSlot', key)
        store_value(obj, 'temperatureInstant', value)
        db[key] = obj

def gen_table() -> list:
    rows: list = []
    for k, v in db.items():
        row: dict = {}
        objects: OrderedDict = OrderedDict()
        store_value(objects, 'controlSlot', v.get('controlSlot'))
        store_value(objects, 'temperatureInstant', v.get('temperatureInstant'))
        row['objects'] = objects
        rows.append(row)
    return rows

def snmp_main(in_json_str: str) -> str:
    global db
    db = {}

    in_json = json.loads(in_json_str)
    snmp_info = in_json.get('_snmp_info_')
    utilities.process_snmp_info(snmp_info)

    platform = in_json.get('platform', {})
    data = platform.get('temperature', []) or in_json.get('temperature', [])

    store_data(data)

    response: dict = {'tables': {}}
    if utilities.is_table_enabled('nokiaControlTemperatureTable'):
        response['tables']['nokiaControlTemperatureTable'] = gen_table()

    return json.dumps(response, separators=(',', ':'))
