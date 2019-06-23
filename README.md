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