#!/usr/bin/python
#
# Copyright 2011 Gavin Bunney.
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
import urllib2
import feedparser
import time

BAMBOO_BUILD_KEY = 'RACQICTPCC-BUILDTRUNK'
#BAMBOO_BUILD_KEY = 'RACQICTPCC-DBSTATISTICS'
BAMBOO_HOST      = '10.53.116.60'
BAMBOO_PORT      = '8085'
BAMBOO_USERNAME  = 'gbunney'
BAMBOO_PASSWORD  = 'gbunney'
BAMBOO_RSS_URL   = 'http://%s:%s/rss/createAllBuildsRssFeed.action?feedType=rssFailed&buildKey=%s' % (BAMBOO_HOST, BAMBOO_PORT, BAMBOO_BUILD_KEY)

LATEST_BUILD      = dict()
LATEST_BUILD_GUID = None
PREV_LATEST_BUILD_GUID = None

############################################################################
# Retrieve the bamboo feed.
############################################################################
def retrieve_bamboo_feed():
  auth = urllib2.HTTPBasicAuthHandler()
  auth.add_password(BAMBOO_HOST, BAMBOO_HOST, BAMBOO_USERNAME, BAMBOO_PASSWORD)
  global BUILD_FEED
  BUILD_FEED = feedparser.parse(BAMBOO_RSS_URL, handlers=[auth])
 
  global LATEST_BUILD
  global LATEST_BUILD_GUID
  global PREV_LATEST_BUILD_GUID

#  PREV_LATEST_BUILD_GUID = LATEST_BUILD_GUID 

  if len(BUILD_FEED.entries) > 0:
    LATEST_BUILD = BUILD_FEED.entries[0]
    LATEST_BUILD_GUID = LATEST_BUILD.guid

############################################################################
# Detect builds that have failed
############################################################################
def detect_failed_builds():
  while True:
    try:
      retrieve_bamboo_feed()
      if PREV_LATEST_BUILD_GUID != LATEST_BUILD_GUID:
        print 'found new failed build!!'
        print LATEST_BUILD.title

      print 'waiting...'

      description = LATEST_BUILD.description
      lastIdx = 0
      userSearchKey = '/browse/user/'
      while description.find(userSearchKey, lastIdx) >= 0 and description.find(".</p>") > description.find(userSearchKey, lastIdx):
        userIdx = description.find(userSearchKey, lastIdx)
        userEndIdx = description.find(">", userIdx) - 1
        print description[userIdx+len(userSearchKey) : userEndIdx]
        lastIdx = description.find(userSearchKey, lastIdx) + 1

      #time.sleep(15)
      break
    except:
      print 'bye!'
      break

retrieve_bamboo_feed()
detect_failed_builds()
