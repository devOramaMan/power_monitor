#
#start at startup
#sudo vi /etc/rc.local
#sudo python -u /home/lun/power_monitor/power_price/power_price_deamon.py 2>&1 /home/lun/power_monitor/power_price/log.txt &
#

from datetime import datetime, timedelta
import sys
import requests

import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
#Påslag øre i abonomang
ABO_PRICE_KR=2.80/100
MVA=1.25

REST_CODE = {
200:"OK",
202:"Accepted",
204:"No Content",
400:"Bad Request",
404:"Not Found"
}

REST_OK = 200
REST_ACCEPTED = 202

url = "http://192.168.10.137:8086"
bucket = "Home"
token = ""
orgid = "4f37428e4085d8e2"
#"tagset": [],
authtoken = "azEnZHCUW24OFSszKP7x1JagkdfUCJeIA-0lduU-jzHhS-zDXu9FyQ9R6ICXdT8Q92GeQmgbBYIF_lNgU-PScQ=="
#"begdate": 1667257200

client = influxdb_client.InfluxDBClient(
   url=url,
   token=authtoken,
   org=orgid
)

# Write script
write_api = client.write_api(write_options=SYNCHRONOUS)
#p = influxdb_client.Point.measurement("pw_price_nok").field("val", 1.14).time("2023-09-06T18:30:00.224Z")
#write_api.write(bucket=bucket, org=orgid, record=p)



def parse_price(url):
    r = requests.get(url=url )
    if r.status_code in REST_CODE:
        print("url return code %s " % REST_CODE[r.status_code])
    else:
        print("status code %s " % r.status_code)

    
    if r.status_code == REST_ACCEPTED or r.status_code == REST_OK:
        file = r.json()
        for element in file:
            val = ((element['NOK_per_kWh']*MVA)+ABO_PRICE_KR)
            time = element['time_start'][:-6]+".0Z"
            #print("val %f %s" % (val, time))

            p = influxdb_client.Point.measurement("pw_price_nok").field("val", val).time(time)
            write_api.write(bucket=bucket, org=orgid, record=p)
        return 0
    else:
        return 1

def from_date(dtg):
    now = datetime.now()
    tonow = (now.year, now.month,now.day)
    next = (dtg.year, dtg.month,dtg.day)
    print("start %s..." %  dtg.strftime('%Y-%m-%d %H:%M:%S'))
    nextdtg = dtg
    try:
        while(next != tonow):
            URL_HVA_KOSTER="https://www.hvakosterstrommen.no/api/v1/prices/%d/%.2d-%.2d_NO1.json" % next
            parse_price(URL_HVA_KOSTER)
            time.sleep(1)
            nextdtg = nextdtg + timedelta(days=1)
            print("next %s..." %  nextdtg.strftime('%Y-%m-%d %H:%M:%S'))
            next = (nextdtg.year, nextdtg.month,nextdtg.day)
            time.sleep(1)

        URL_HVA_KOSTER="https://www.hvakosterstrommen.no/api/v1/prices/%d/%.2d-%.2d_NO1.json" % next
        parse_price(URL_HVA_KOSTER)
        nextdtg = nextdtg + timedelta(days=1)
        print("next %s..." %  nextdtg.strftime('%Y-%m-%d %H:%M:%S'))
        next = (nextdtg.year, nextdtg.month,nextdtg.day)
        parse_price(URL_HVA_KOSTER)
    except Exception as err:
        print("Exception occurred %s" % err)




if __name__ == "__main__":
    if (len(sys.argv)>1):

        try:
            print("Update el price input arg %s..." %  str(sys.argv[1:]))
            dtg = datetime.strptime(sys.argv[1], "%Y-%m-%d")
            #print("dtg %s..." %  dtg.strftime('%Y-%m-%d %H:%M:%S'))
            from_date(dtg)
        except:
            print("failed to update")

    

