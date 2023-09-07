<h1>Household Power Monitor</h1>
<p>The following contains explanatory to setup our household power monitor. It is used to get a overview of current consumption in our apartment and the apartment under.</p>

![sokkel](./sokkel.png)

<h3>Parts:</h3>
<li>Rpi4b</li>
<li>Iotawatt</li>
<li>Humidity Sensor(s)</li>
<li>UPS</li>

<h3>Setup:</h3>
<h5>Iotawatt config</h5>
<li>./iotawatt/config.txt</li>

<h5>RPI installation:</h5>

```shell
wget -O- https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/grafana-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/grafana-archive-keyring.gpg] https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update && sudo apt install -y grafana
sudo systemctl unmask grafana-server.service
sudo systemctl start grafana-server
sudo systemctl enable grafana-server.service
influx
wget -qO- https://repos.influxdata.com/influxdb.key | gpg --dearmor | sudo tee /usr/share/keyrings/influx-archive-keyring.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/influx-archive-keyring.gpg] https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt update && sudo apt install -y influxdb
sudo systemctl unmask influxdb.service
sudo systemctl start influxdb
sudo systemctl enable influxdb.service
influx
sudo service influxdb status
wget -qO- https://repos.influxdata.com/influxdb.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null
export DISTRIB_ID=$(lsb_release -si); export DISTRIB_CODENAME=$(lsb_release -sc)
echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg]
https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list > /dev/null
sudo apt-get update && sudo apt-get install influxdb2
wget -qO- https://repos.influxdata.com/influxdb.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null
export DISTRIB_ID=$(lsb_release -si); export DISTRIB_CODENAME=$(lsb_release -sc)
echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list > /dev/null
sudo apt-get update && sudo apt-get install influxdb2
sudo /usr/share/influxdb/influxdb2-upgrade.sh
```

<h5>Grafana configuration:</h5>
<li>./grafana/db_config.json</li>
<li>./grafana/Sokkel_1.1-1693041894446.json</li>

<h5>Hardware schema:</h5>
<li>./hw</li>

<h5>Update influxdb with the power price for the next day once a day:</h5>
<li>./power_price</li>
