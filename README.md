# Greenhouse control with IoT Core

## Setup

### Required files

`publisher/credentials.json`
```json
{
  "registry_id": "",
  "cloud_region": "europe-west1",
  "project_id": "",
  "device_id": "test-device",
  "algorithm": "RS256",
  "private_key_file": "rsa_private.pem",
  "ca_certs": "roots.pem",
  "mqtt_bridge_hostname": "mqtt.googleapis.com",
  "mqtt_bridge_port": 8883,
  "num_messages": 40,
  "jwt_expires_minutes": 20,
  "message_type": ""
}
```

`publisher/roots.pem`

`publisher/rsa_private.pem`

Get `roots.pem` by running: 
```bash
wget https://pki.goog/roots.pem
```
 or 
```bash
curl https://pki.goog/roots.pem > roots.pem
```

`subscriber/credentials.json`
```json
{
  "API_SCOPES": ["https://www.googleapis.com/auth/cloud-platform"],
  "API_VERSION": "v1",
  "DISCOVERY_API": "https://cloudiot.googleapis.com/$discovery/rest",
  "SERVICE_NAME": "cloudiot",
  "pubsub_subscription": "",
  "project_id": "",
  "service_account_json": "./gcp-credentials.json"
}
```


## Raspberry Pi

To run script on startup.
* `sudo cp publisher/pi/publisher.service /etc/systemd/system/publisher.service`

* `sudo systemctl start publisher.service`

* `sudo systemctl enable publisher.service`

## Docker commands

`docker run --rm -d --name some-timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb:latest-pg11`

`docker run -it --net=host --rm timescale/timescaledb psql -h localhost -U postgres`

`docker-compose build --force-rm && docker-compose up --force-recreate --renew-anon-volumes`

To rebuild sql scripts
`docker-compose build && docker-compose up --renew-anon-volumes`