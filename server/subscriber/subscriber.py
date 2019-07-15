r"""Sample server that pushes configuration to Google Cloud IoT devices.

This example represents a server that consumes telemetry data from multiple
Cloud IoT devices. The devices report telemetry data, which the server consumes
from a Cloud Pub/Sub topic. The server then decides whether to turn on or off
individual devices fans.

This example requires the Google Cloud Pub/Sub client library. Install it with

  $ pip install --upgrade google-cloud-pubsub

If you are running this example from a Compute Engine VM, you will have to
enable the Cloud Pub/Sub API for your project, which you can do from the Cloud
Console. Create a pubsub topic, for example
projects/my-project-id/topics/my-topic-name, and a subscription, for example
projects/my-project-id/subscriptions/my-topic-subscription.

Windows
set GOOGLE_APPLICATION_CREDENTIALS=.\gcp-credentials.json
Linux
export GOOGLE_APPLICATION_CREDENTIALS=.\gcp-credentials.json

You can then run the example with

  $ python cloudiot_pubsub_example_server.py \
    --project_id=my-project-id \
    --pubsub_subscription=my-topic-subscription \
"""

import base64
import json
import os
import sys
from threading import Lock
import time

from google.cloud import pubsub
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials


class Server(object):
    """Represents the state of the server."""

    def __init__(self, callback):
        self.callback_func = callback
        with open('configuration.json') as json_file:
            config = json.load(json_file)
        self.api_scopes = config['API_SCOPES']
        self.api_version = config['API_VERSION']
        self.discovery_api = config['DISCOVERY_API']
        self.service_name = config['SERVICE_NAME']
        self.pubsub_subscription = config['pubsub_subscription']
        self.project_id = config['project_id']
        self.service_account_json = config['service_account_json']

        self.subscription_path = ('projects/{}/subscriptions/{}'.format(
            self.project_id,
            self.pubsub_subscription,))
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.service_account_json, self.api_scopes)

        if not self.credentials:
            sys.exit('Could not load service account credential '
                     'from {}'.format(self.service_account_json))

        discovery_url = '{}?version={}'.format(
            self.discovery_api, self.api_version)

        self._service = discovery.build(
            self.service_name,
            self.api_version,
            discoveryServiceUrl=discovery_url,
            credentials=self.credentials,
            cache_discovery=False)

        # Used to serialize the calls to the
        # modifyCloudToDeviceConfig REST method. This is needed
        # because the google-api-python-client library is built on top
        # of the httplib2 library, which is not thread-safe. For more
        # details, see: https://developers.google.com/
        #     api-client-library/python/guide/thread_safety
        self._update_config_mutex = Lock()

    def _update_device_config(self, project_id, region, registry_id, device_id,
                              data):
        """Push the data to the given device as configuration."""
        config_data = None
        print('The device ({}) has a temperature '
              'of: {}'.format(device_id, data['temperature']))
        if data['temperature'] < 0:
            # Turn off the fan.
            config_data = {'fan_on': False}
            print('Setting fan state for device', device_id, 'to off.')
        elif data['temperature'] > 10:
            # Turn on the fan
            config_data = {'fan_on': True}
            print('Setting fan state for device', device_id, 'to on.')
        else:
            # Temperature is OK, don't need to push a new config.
            return

        config_data_json = json.dumps(config_data)
        body = {
            # The device configuration specifies a version to update, which
            # can be used to avoid having configuration updates race. In this
            # case, you use the special value of 0, which tells Cloud IoT to
            # always update the config.
            'version_to_update': 0,
            # The data is passed as raw bytes, so you encode it as base64.
            # Note that the device will receive the decoded string, so you
            # do not need to base64 decode the string on the device.
            'binary_data': base64.b64encode(
                config_data_json.encode('utf-8')).decode('ascii')
        }

        device_name = ('projects/{}/locations/{}/registries/{}/'
                       'devices/{}'.format(
                           project_id,
                           region,
                           registry_id,
                           device_id))

        request = self._service.projects().locations().registries().devices(
        ).modifyCloudToDeviceConfig(name=device_name, body=body)

        # The http call for the device config change is thread-locked so
        # that there aren't competing threads simultaneously using the
        # httplib2 library, which is not thread-safe.
        self._update_config_mutex.acquire()
        try:
            request.execute()
        except HttpError as e:
            # If the server responds with a HtppError, log it here, but
            # continue so that the message does not stay NACK'ed on the
            # pubsub channel.
            print('Error executing ModifyCloudToDeviceConfig: {}'.format(e))
        finally:
            self._update_config_mutex.release()

    def run(self):
        """The main loop. Consumes messages from the
        Pub/Sub subscription.
        """

        subscriber = pubsub.SubscriberClient()

        def callback(message):
            """Logic executed when a message is received from
            subscribed topic.
            """
            try:
                data = json.loads(message.data.decode('utf-8'))
            except ValueError as e:
                print('Loading Payload ({}) threw an Exception: {}.'.format(
                    message.data, e))
                message.ack()
                return

            # Get the registry id and device id from the attributes. These are
            # automatically supplied by IoT, and allow the server to determine
            # which device sent the event.
            device_project_id = message.attributes['projectId']
            device_region = message.attributes['deviceRegistryLocation']
            device_registry_id = message.attributes['deviceRegistryId']
            device_id = message.attributes['deviceId']
            self.callback_func(data)
            # print(data)
            # Send the config to the device.
            # self._update_device_config(
            #     device_project_id,
            #     device_region,
            #     device_registry_id,
            #     device_id,
            #     data)

            # Acknowledge the consumed message. This will ensure that they
            # are not redelivered to this subscription.
            message.ack()

        print('Listening for messages on {}'.format(self.subscription_path))
        subscriber.subscribe(self.subscription_path, callback)

        # The subscriber is non-blocking, so keep the main thread from
        # exiting to allow it to process messages in the background.
        while True:
            time.sleep(60)


def printer(data):
    print(data)


def main():
    server = Server(printer)
    server.run()


if __name__ == '__main__':
    main()
