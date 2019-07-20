Sample device that consumes configuration from Google Cloud IoT.
This example represents a simple device with a temperature sensor and a fan
(simulated with software). When the device's fan is turned on, its temperature
decreases by one degree per second, and when the device's fan is turned off,
its temperature increases by one degree per second.

Every second, the device publishes its temperature reading to Google Cloud IoT
Core. The server meanwhile receives these temperature readings, and decides
whether to re-configure the device to turn its fan on or off. The server will
instruct the device to turn the fan on when the device's temperature exceeds 10
degrees, and to turn it off when the device's temperature is less than 0
degrees. In a real system, one could use the cloud to compute the optimal
thresholds for turning on and off the fan, but for illustrative purposes we use
a simple threshold model.

To connect the device you must have downloaded Google's CA root certificates,
and a copy of your private key file. See cloud.google.com/iot for instructions
on how to do this. Run this script with the corresponding algorithm flag.

  $ python cloudiot_pubsub_example_mqtt_device.py \
      --project_id=my-project-id \
      --registry_id=example-my-registry-id \
      --device_id=my-device-id \
      --private_key_file=rsa_private.pem \
      --algorithm=RS256

With a single server, you can run multiple instances of the device with
different device ids, and the server will distinguish them. Try creating a few
devices and running them all at the same time.