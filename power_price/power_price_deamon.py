#
#start at startup
#sudo vi /etc/rc.local
#sudo python -u /home/lun/power_monitor/power_price/power_price_deamon.py 2>&1 /home/lun/power_monitor/power_price/log.txt &
#


from datetime import datetime, timedelta
import os
import sys

import os



try:
    dtgname = "./log_%s.txt" % datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    os.rename("./log.txt", dtgname)
    print("move log to file %s" % dtgname, flush=True)
except:
    pass

sys.stdout = open('./log.txt', 'w')
sys.stderr = sys.stdout

print("Starting el price process %s..." %  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)

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
        print("url return code %s " % REST_CODE[r.status_code], flush=True)
    else:
        print("status code %s " % r.status_code, flush=True)

    
    if r.status_code == REST_ACCEPTED or r.status_code == REST_OK:
        file = r.json()
        for element in file:
            val = ((element['NOK_per_kWh']*MVA)+ABO_PRICE_KR)
            time = element['time_start'][:-6]+".0Z"
            p = influxdb_client.Point.measurement("pw_price_nok").field("val", val).time(time)
            write_api.write(bucket=bucket, org=orgid, record=p)

    return file
if __name__ == "__main__":
    exception_cnt = 0
    last_exception = None
    first_exception = None
    last = datetime.now()
    while(True):
        now = datetime.now() + timedelta(days=1)
        try:
            if ( ((now - last).total_seconds()/3600 ) > 24 ) and ( now.hour > 19 ):
                print("Update Db with electricity prices", flush=True)
                URL_HVA_KOSTER="https://www.hvakosterstrommen.no/api/v1/prices/%d/%.2d-%.2d_NO1.json" % (now.year, now.month,now.day )
                last = now
                parse_price(URL_HVA_KOSTER)
                if exception_cnt:
                    print("clear exception count %d" % exception_cnt, flush=True)
                    exception_cnt = 0
            print("Sleep %s..." %  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)
            time.sleep(3600)
            print("Wakeup %s..." %  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)
        except Exception as err:
            print("unexpected exception ocurred err: %s" % err, flush=True)

            if exception_cnt > 10: 
                if ((now - first_exception).total_seconds()/3600 > 20):
                    #restart process if more than 10 exceptions occurred
                    #and it is less than 20 hours since the first exception
                    os.execv(sys.argv[0], sys.argv)

            if exception_cnt == 0:
                first_exception = datetime.now()

            exception_cnt += 1
            
            time.sleep(1300)
            print("Wakeup from exception %s..." %  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), flush=True)
        except KeyboardInterrupt:
            print('KeyboardInterrupt %d' % exception_cnt, flush=True)
            exception_cnt += 1
            if exception_cnt > 2:
                try:
                    sys.exit(130)
                except SystemExit:
                    os._exit(130)



