#!/usr/bin/python

import sys
import datetime
import csv
from unifi.controller import *
# stores unifi controller info
import config

# list of sites
# this is what appears on the unifi web management url as such,
# https://unifi.ccfls.org:8443/manage/s/benson/statistics
# the site name in this example is benson
# note that MPL is default
sites = ['benson','cambridgesprings','cochrantonwireless','linesville','default','saegertown','shontz','springboro','stone']

# take note of the date
today = datetime.date.today()
# take note of yesterday
yesterday = today - datetime.timedelta(days=1)
# now check if a yearly report is needed
# if today is the first day of the year, then the report is needed
yearly = 0
if today.year != yesterday.year:
        yearly = 1

def get_api_controller(site):
    return Controller(config.ip,config.uname,config.pswd,config.port,config.version,site)

def write_csv(data,site,yearly):
    if yearly == 0:
        with open(site+today.strftime("%Y-%m")+".csv", "w") as file:
            file.write('date,users,bytes\n')
            for item in data:
                if 'num_sta' in item:
                    file.write(str(datetime.date.fromtimestamp(item["time"]/1000))+','+str(item["num_sta"])+','+str(item["bytes"])+'\n')
    

def process_site(site):
    api = get_api_controller(site)

    # first, we'll perform a monthly report for the past month
    # get the latest possible time from yesterday for the end time
    dt = datetime.datetime.combine(yesterday,datetime.time.max)
    # convert to unix timestamp
    endtime = float(dt.strftime("%s"))
    # calculate report duration
    duration = datetime.datetime.combine(yesterday.replace(day=1),datetime.time.min)
    # convert to timestamp
    duration = endtime - float(duration.strftime("%s"))

    # now, call the unifi api to get the data in json format
    data = api.get_daily_statistics(endtime,duration)

    # write the data to a csv file
    write_csv(data,site,yearly)

# iterate through all sites, writing out report files
for site in sites:
    process_site(site)
