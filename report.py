#!/usr/bin/python

import datetime
from os.path import basename
# needed for email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
# unifi api from https://github.com/unifi-hackers/unifi-api
from unifi.controller import *
# stores unifi controller info
import config

# first, the dictionary of library names, email addresses to send reports, and 
# the unifi site name
# the site is what appears on the unifi web management url as such,
# https://unifi.ccfls.org:8443/manage/s/benson/statistics
# the site name in this example is benson
# note that MPL is default
# the email field will be where reports for this library are sent
# the name field is how the library name will appear on the report for formatting purposes

itAddr = "cmurdock@ccfls.org"
fromAddr = "unifi@ccfls.org"

libs = [{'site':'benson','email':'justin.hoenke@ccfls.org','name':'Benson'},
        {'site':'cambridgesprings','email':'cspl@ccfls.org','name':'Cambridge'},
        {'site':'cochrantonwireless','email':'capl@ccfls.org','name':'Cochranton'},
        {'site':'linesville','email':'lcpl@ccfls.org','name':'Linesville'},
        {'site':'default','email':'aporter@ccfls.org','name':'Meadville'},
        {'site':'saegertown','email':'sal@ccfls.org','name':'Saegertown'},
        {'site':'shontz','email':'shontpl@ccfls.org','name':'Shontz'},
        {'site':'springboro','email':'springboropl@ccfls.org','name':'Springboro'},
        {'site':'stone','email':'stone@ccfls.org','name':'Stone'}]

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
        with open(site+today.strftime("%Y-%m")+".csv", "r+") as file:
            file.write('Date,Users,Gigabytes\n')
            for item in data:
                if 'num_sta' in item:
                    file.write(str(datetime.date.fromtimestamp(item["time"]/1000))+','+str(item["num_sta"])+','+str(item["bytes"]*1e-9)+'\n')

            msg = MIMEMultipart()
            msg['Subject']= 'Wifi Usage Report'
            msg['From'] = fromAddr
            #msg['To'] = ', '.join([site['email'],itAddr])
            msg['To'] = ', '.join(['royokou@gmail.com'])
            msg.attach(MIMEText(site+' wifi usage for '+today.strftime("%Y-%m")))

            msg.attach(MIMEApplication(
                file.read(),
                Content_Disposition='attachment; filename="%s"' % basename(file),
                Name=basename(file)
                ))

            s = smtplib.SMTP('smtp-relay.gmail.com')
            #s.sendmail(fromAddr,[site['email'],itAddr],msg.as_string())
            s.sendmail(fromAddr,['royokou@gmail.com'],msg.as_string())
            s.quit()

def process_site(lib):
    api = get_api_controller(lib['site'])

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
    write_csv(data,lib['name'],yearly)

# iterate through all sites, writing out report files
for lib in libs:
    process_site(lib)
