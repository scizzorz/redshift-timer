from datetime import datetime
import astral
import json
import os
import pytz
import sys
import time

if len(sys.argv) < 2:
  print('Please give a config file :(', file=sys.stderr)
  sys.exit(1)

with open(sys.argv[1]) as fp:
  config = json.load(fp)

loc = astral.Location()
loc.name = config['city']
loc.region = config['region']
loc.timezone = config['timezone']
loc.latitude = config['latitude']
loc.longitude = config['longitude']
loc.elevation = config['elevation']

tz = pytz.timezone(loc.timezone)

night = config['night']
day = config['day']


def ease_up(amt, low, high):
  '''Cubic easing out'''

  amt -= 1
  return (high - low) * (amt * amt * amt + 1) + low


def ease_down(amt, low, high):
  '''Cubic easing in'''

  return high - (amt * amt * amt) * (high - low)


try:
  while True:
    now = tz.localize(datetime.now())
    suntimes = loc.sun(date=now)

    print('    Now:', now.strftime('%I:%M%P'))
    print('   Dawn:', suntimes['dawn'].strftime('%I:%M%P'))
    print('Sunrise:', suntimes['sunrise'].strftime('%I:%M%P'))
    print('   Noon:', suntimes['noon'].strftime('%I:%M%P'))
    print(' Sunset:', suntimes['sunset'].strftime('%I:%M%P'))
    print('   Dusk:', suntimes['dusk'].strftime('%I:%M%P'))

    # always night before dawn
    if now < suntimes['dawn']:
      temp = night
      print('night', '->', temp)

    # always night after dusk
    elif now > suntimes['dusk']:
      temp = night
      print('night', '->', temp)

    # dawn -> noon
    elif now < suntimes['noon']:
      elapsed = now - suntimes['dawn']
      morning = suntimes['noon'] - suntimes['dawn']
      fade = elapsed.total_seconds() / morning.total_seconds()
      temp = int(ease_up(fade, night, day))
      print('morning', fade, '->', temp)

    # noon -> dusk
    else:
      elapsed = now - suntimes['noon']
      evening = suntimes['dusk'] - suntimes['noon']
      fade = 1 - elapsed.total_seconds() / evening.total_seconds()
      temp = int(ease_up(fade, night, day))
      print('evening', fade, '->', temp)

    # apply redshift
    os.system('redshift -O {}'.format(temp))
    time.sleep(60)

except KeyboardInterrupt:
  # reset redshift
  os.system('redshift -O 6500')
