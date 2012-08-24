#!/usr/bin/python
#
# Copyright 2011 Gavin Bunney
# 
# Based on retaliation.py by PaperCut Software Int. Pty. Ltd. 
# Copyright 2011 PaperCut Software Int. Pty. Ltd. http://www.papercut.com/
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# 

############################################################################
# 
# Ikara - Bamboo Blame!
#
############################################################################

import sys
import time

import usb.core
import usb.util

import urllib2
import feedparser

##########################  CONFIG   #########################

#
# Define a dictionary of "command sets" that map usernames to a sequence 
# of commands to target the user (e.g their desk/workstation).  It's 
# suggested that each set start and end with a "zero" command so it's
# always parked in a known reference location. The timing on move commands
# is milli-seconds. The number after "fire" denotes the number of rockets
# to shoot.
#
COMMAND_SETS = {
    #"Peter Do" : (
    #    ("right", 2000),
    #    ("fire", 1),
    #    ("zero", 0),
    #),
    "Patrick Simon" : (
        ("right", 1250),
        ("up", 200),
        ("fire", 1),
        ("zero", 0),
    ),
    "Priyath Sandanayake" : (
        ("right", 1250),
        ("up", 800),
        ("fire", 1),
        ("zero", 0),
    ),
    "Chris Greben" : (
        ("right", 2100),
        ("up", 500),
        ("fire", 1),
        ("zero", 0),
    ),
    "Paul Bevis" : (
        ("right", 2700),
        ("up", 300),
        ("fire", 1),
        ("zero", 0),
    ),
    "Tom Romano" : (
        ("right", 3000),
        ("up", 350),
        ("fire", 1),
        ("zero", 0),
    ),
#    "Andy Souyave" : (
#        ("right", 5000),
#        ("up", 1000),
#        ("fire", 1),
#        ("zero", 0),
#    ),
    "Gavin Bunney" : (
        ("right", 3500),
        ("up", 350),
        ("fire", 1),
        ("zero", 0),
    ),

}

BAMBOO_HOST      = '10.53.116.60'
BAMBOO_PORT      = '8085'
BAMBOO_USERNAME  = 'gbunney'
BAMBOO_PASSWORD  = 'gbunney'
##########################  ENG CONFIG  #########################

# The code...

# Protocol command bytes
DOWN    = 0x01
UP      = 0x02
LEFT    = 0x04
RIGHT   = 0x08
FIRE    = 0x10
STOP    = 0x20

DEVICE = None

BUILD_KEYS        = list()
BUILDS            = dict()
BAMBOO_RSS_URL    = ''

########################################################################################################################
def usage():
    print "Usage: ikara.py [command] [value]"
    print ""
    print "   commands:"
    print "     monitor - poll the bamboo rss feed for new failed builds,"
    print "               for the comma seperated list of build-keys"
    print ""
    print "     up    - move up <value> milliseconds"
    print "     down  - move down <value> milliseconds"
    print "     right - move right <value> milliseconds"
    print "     left  - move left <value> milliseconds"
    print "     fire  - fire <value> times (between 1-4)"
    print "     zero  - park at zero position (bottom-left)"
    print "     pause - pause <value> milliseconds"
    print ""
    print "     <command_set_name> - run/test a defined COMMAND_SET"
    print "             e.g. run:"
    print "                  ikara.py 'Snappy Tom'"
    print "             to test targeting of 'Snappy Tom' as defined in your command set."
    print ""

########################################################################################################################
def setup_usb():
    # Tested only with the Cheeky Dream Thunder
    global DEVICE 
    DEVICE = usb.core.find(idVendor=0x2123, idProduct=0x1010)

    if DEVICE is None:
        raise ValueError('Missile device not found')

    DEVICE.set_configuration()

########################################################################################################################
def send_cmd(cmd):
    DEVICE.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])

########################################################################################################################
def send_move(cmd, duration_ms):
    send_cmd(cmd)
    time.sleep(duration_ms / 1000.0)
    send_cmd(STOP)

########################################################################################################################
def run_command(command, value):
    command = command.lower()
    if command == "right":
        send_move(RIGHT, value)
    elif command == "left":
        send_move(LEFT, value)
    elif command == "up":
        send_move(UP, value)
    elif command == "down":
        send_move(DOWN, value)
    elif command == "zero" or command == "park" or command == "reset":
        # Move to bottom-left
        send_move(DOWN, 2000)
        send_move(LEFT, 8000)
    elif command == "pause" or command == "sleep":
        time.sleep(value / 1000.0)
    elif command == "fire" or command == "shoot":
        if value < 1 or value > 4:
            value = 1
        # Stabilize prior to the shot, then allow for reload time after.
        time.sleep(0.5)
        for i in range(value):
            send_cmd(FIRE)
            time.sleep(4.5)
    else:
        print "Error: Unknown command: '%s'" % command

########################################################################################################################
def run_command_set(commands):
    for cmd, value in commands:
        run_command(cmd, value)

########################################################################################################################
def retrieve_bamboo_feed():

  auth = urllib2.HTTPBasicAuthHandler()
  auth.add_password(BAMBOO_HOST, BAMBOO_HOST, BAMBOO_USERNAME, BAMBOO_PASSWORD)

  global BUILDS
  for buildKey in BUILD_KEYS:

    buildFeed = feedparser.parse(BAMBOO_RSS_URL + buildKey, handlers=[auth])

    if buildKey in BUILDS:
      BUILDS[buildKey]['previous_latest_guid'] = BUILDS[buildKey]['latest_guid']
    else:
      BUILDS[buildKey] = dict(latest_build = dict(), latest_guid = None, previous_latest_guid = None)

    if len(buildFeed.entries) > 0:
      BUILDS[buildKey]['latest_build'] = buildFeed.entries[0]
      BUILDS[buildKey]['latest_guid'] = buildFeed.entries[0].guid

########################################################################################################################
def target_user(user):
    match = False
    for key in COMMAND_SETS:
        if key.lower() == user.lower():
            # We have a command set that targets our user so got for it!
            run_command_set(COMMAND_SETS[key])
            match = True
            break
    if not match:
        print "WARNING: No target command set defined for user %s" % user

########################################################################################################################
def detect_failed_builds():
  while True:
    try:
      retrieve_bamboo_feed()
      offending_users = set()

      for buildKey in BUILD_KEYS:
        build = BUILDS[buildKey]

        if build['previous_latest_guid'] is not None and build['previous_latest_guid'] != build['latest_guid']:
          print build['latest_build']['title']

          description = build['latest_build']['description']
          lastIdx = 0
          userSearchKey = ' made the following changes at '
          while description.find(userSearchKey, lastIdx) >= 0:
            userEndIdx = description.find(userSearchKey, lastIdx)
            userStartIdx = description.rfind("\n", 0, userEndIdx)
            offending_users.add(description[userStartIdx : userEndIdx].lstrip().rstrip())
            lastIdx = description.find(userSearchKey, lastIdx) + 1

      for user in offending_users:
        print 'Targeting ' + user
        target_user(user)

      print 'Waiting for Bamboo failed builds...'
      time.sleep(5)

    except KeyboardInterrupt:
      print 'bye!'
      break

########################################################################################################################
def main(args):

    if len(args) < 2:
        usage()
        sys.exit(1)

    setup_usb()

    if args[1] == "monitor":
      if len(args) != 3:
        print "Specify the Build Key(s) to watch"
        sys.exit(1)
      
      print "Waiting for Bamboo failed builds..."
      global BUILD_KEYS
      BUILD_KEYS = args[2].split(',')
      global BAMBOO_RSS_URL
      BAMBOO_RSS_URL = 'http://%s:%s/rss/createAllBuildsRssFeed.action?feedType=rssFailed&buildKey=' % (BAMBOO_HOST, BAMBOO_PORT)
      
      detect_failed_builds()
      # Will never return
      return

    # Process any passed commands or command_sets
    command = args[1]
    value = 0
    if len(args) > 2:
        value = int(args[2])

    if command in COMMAND_SETS:
        run_command_set(COMMAND_SETS[command])
    else:
        run_command(command, value)


if __name__ == '__main__':
    main(sys.argv)
