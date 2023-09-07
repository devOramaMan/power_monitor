#
#start at startup
#sudo vi /etc/rc.local
#sudo python /home/lun/power_monitor/power_price/power_price_deamon.py &
#

import requests
from datetime import datetime, timedelta
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
#Påslag øre i abonomang
ABO_PRICE_KR=2.80/100
MVA=1.25




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
    r.status_code

    file = r.json()
    for element in file:
        val = (element['NOK_per_kWh']*ABO_PRICE_KR*MVA)
        time = element['time_start'][:-6]+".0Z"
        p = influxdb_client.Point.measurement("pw_price_nok").field("val", val).time(time)
        write_api.write(bucket=bucket, org=orgid, record=p)

    return file

last = datetime.now()
while(True):
    now = datetime.now() + timedelta(days=1)
    if ( ((now - last).total_seconds()/3600 ) > 24 ) and ( now.hour > 19 ):
        print("Update Db with electricity prices")
        URL_HVA_KOSTER="https://www.hvakosterstrommen.no/api/v1/prices/%d/%.2d-%.2d_NO1.json" % (now.year, now.month,now.day )
        last = now
        parse_price(URL_HVA_KOSTER)
    print("Sleep %s...\n" %  datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time.sleep(3600)
    print("Wakeup %s...\n" %  datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


