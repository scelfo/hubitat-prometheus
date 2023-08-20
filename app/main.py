import json
import logging
import os
import urllib.request

from flask import Flask, render_template
app = Flask(__name__)

# Required url from the 'Get All Devices with Full Details' link on the Hubitat Maker API app.
hubitat_url = os.getenv('HUBITAT_MAKER_API_ALL_DEVICES_FULL_DETAILS_URL', None)

# Prefix that will be set on the prometheus metrics.
metric_prefix = os.getenv('HUBITAT_METRIC_PREFIX', 'hubitat')

# Optional setting for https://flumewater.com sensors.
flume_device_names = os.getenv('HUBITAT_FLUME_DEVICE_NAMES', None)

@app.route('/metrics')
def get_hubitat_metrics():
  if not metric_prefix:
    raise ValueError('HUBITAT_METRIC_PREFIX must be non-empty!')
  if not hubitat_url:
    raise ValueError('Must set environment variable HUBITAT_MAKER_API_ALL_DEVICES_FULL_DETAILS_URL!')
  response =  json.load(urllib.request.urlopen(hubitat_url))
  airquality_sensors = []
  battery_sensors = []
  contact_sensors = []
  humidity_sensors = []
  motion_sensors = []
  power_sensors = []
  presence_sensors = []
  temperature_sensors = []
  valve_sensors = []
  water_sensors = []
  hvacs = []
  flumes = []
  for item in response:
    if 'AirQuality' in item['capabilities']:
      airquality_sensors.append({
          'name': item['label'],
          'value': item['attributes']['airQuality'],
      })
    if 'Battery' in item['capabilities']:
      battery_sensors.append({
          'name': item['label'],
          'value': item['attributes']['battery'],
      })
    if 'ContactSensor' in item['capabilities']:
      contact_sensors.append({
          'name': item['label'],
          'value': item['attributes']['contact'] == 'open' and 1 or 0,
      })
    if 'MotionSensor' in item['capabilities'] and item['label'] not in ['Kegerator']:
      motion_sensors.append({
          'name': item['label'],
          'value': item['attributes']['motion'] == 'active' and 1 or 0,
      })
    if 'PowerMeter' in item['capabilities']:
      power_sensors.append({
          'name': item['label'],
          'value': item['attributes']['power'],
      })
    if 'PresenceSensor' in item['capabilities'] and item['label'] not in ['Flume']:
      presence_sensors.append({
          'name': item['label'],
          'value': item['attributes']['presence'] == 'present' and 1 or 0,
      })
    if 'RelativeHumidityMeasurement' in item['capabilities'] and item['attributes']['humidity']:
        humidity_sensors.append({
            'name': item['label'],
            'value': item['attributes']['humidity'],
        })
    if 'TemperatureMeasurement' in item['capabilities']:
      temperature_sensors.append({
          'name': item['label'],
          'value': item['attributes']['temperature'],
      })
    if 'Valve' in item['capabilities']:
      valve_sensors.append({
          'name': item['label'],
          'value': item['attributes']['valve'] == 'open' and 1 or 0,
      })
    if 'WaterSensor' in item['capabilities']:
      water_sensors.append({
          'name': item['label'],
          'value': item['attributes']['water'] == 'wet' and 1 or 0,
      })
    if 'ThermostatOperatingState' in item['capabilities']:
      thermostatOperatingState = item['attributes']['thermostatOperatingState']
      value = 0
      if thermostatOperatingState == 'cooling':
        value = 1
      elif thermostatOperatingState == 'heating':
        value = 2
      elif thermostatOperatingState == 'fan only':
        value = 3
      logging.debug('thermostatOperatingState of %s: "%s" -> %d', item['label'], thermostatOperatingState, value)
      hvacs.append({
          'name': item['label'],
          'value': value,
      })
    if flume_device_names and item['name'] in flume_device_names.split(','):
      valve_sensors.append({
          'name': item['label'],
          'value': item['attributes']['flowStatus'] == 'running' and 1 or 0,
      })
      flumes.append({
          'name': item['label'],
          'value': item['attributes']['usageLastMinute'],
      })
  output = render_template('metrics.html',
    metric_prefix=metric_prefix,
    airquality_sensors=airquality_sensors,
    battery_sensors=battery_sensors,
    contact_sensors=contact_sensors,
    humidity_sensors=humidity_sensors,
    motion_sensors=motion_sensors,
    power_sensors=power_sensors,
    presence_sensors=presence_sensors,
    temperature_sensors=temperature_sensors,
    valve_sensors=valve_sensors,
    water_sensors=water_sensors,
    hvacs=hvacs,
    flumes=flumes)
  return '\n'.join([ll.rstrip() for ll in output.splitlines() if ll.strip()])
