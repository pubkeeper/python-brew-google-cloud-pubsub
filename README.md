# Google Cloud Pub/Sub Brew

A brew that allows for the use of [Google Cloud Pub/Sub](https://cloud.google.com/pubsub/) in a Pubkeeper system.

## Example

Example code for publishing/brewing to a GCP topic

```python
from pubkeeper.client import PubkeeperClient
from pubkeeper.brew.google_cloud_pubsub.brew import GoogleCloudPubSubBrew
import json
from time import sleep

client = PubkeeperClient(jwt='token', config={
    'host': '127.0.0.1',
    'port': 9898,
    'secure': False
})

gcp_brew = GoogleCloudPubSubBrew()
gcp_brew.configure({
    'gcp_project': 'project-id',
    'service_account_file': 'service-account-123456.json',
})
client.add_brew(gcp_brew)
client.start()
brewer = client.add_brewer('demo.topic')
try:
    while True:
        sleep(5)
        brewer.brew(json.dumps({'test': 'data'}).encode('utf-8'))
except KeyboardInterrupt:
    client.shutdown()
```

## Configuration

The brew accepts some configuration for connecting to Google Cloud Pub/Sub.

* **gcp_project**
The ID of the GCP project where Google Cloud Pub/Sub is running.

* **service_account_file**
The path to the JSON service account file generated from the [GCP IAM Service Account Page](https://console.cloud.google.com/iam-admin/serviceaccounts). Make sure this service account has permissions to read/write from Google Cloud Pub/Sub

## Topics and Subscriptions

Google Cloud Pub/Sub works by creating "topics" in a project and then creating "subscriptions" that belong to those topics. This maps nicely to Pubkeeper brewers and patrons, respectively, in some ways, but can also create some confusion. Mainly due to the dependency a subscription has on a topic.

This Pubkeeper brew will create a topic in your project, if it does not exist, for every new brewer that is added with a topic. It will never tear down the topics on your behalf. To remove topics from your GCP project you can do so from the Google Cloud Console.

Similarly, the brew will create topic subscriptions whenever a patron receives a `BREWER_NOTIFY` message, if that patron doesn't alreay have a subscription on that topic. When a patron and brewer disconnect the topic subscription will also get torn down from GCP, provided there are no other brewers brewing to that patron on that topic. You can see your active subscriptions on the [GCP Cloud Pub/Sub Subscriptions Page](https://console.cloud.google.com/cloudpubsub/subscriptions). Subscriptions have an ID of `sub.PATRON_ID.TOPIC` where `PATRON_ID` is the ID of the patron listening to that subscription and `TOPIC` is the Pubkeeper topic of the subscription.

## Known Limitations

### Multiple Brewers, One Patron
There is currently a limitation within the Pubkeeper client that makes it difficult for multiple brewers to brew to the same patron on the same topic when using a shared communication channel like GCP Pub/Sub. See [this PR](https://github.com/pubkeeper/python-client/pull/57) for more details. This means that, in its current state, if one patron is subscribed to a single topic that multiple brewers are brewing too, it may not receive all of the messages brewed to that topic. To workaround, use different sub-topics for each brewer and subscribe to the wildcard at the patron.

Example:
Instead of this setup:
```
+----------------+
|    Brewer 1    |
|   demo.topic   +-----+
|                |     |    +-----------------+
+----------------+     |    |      Patron     |
                       +---->    demo.topic   |
+----------------+     |    |                 |
|    Brewer 2    |     |    +-----------------+
|   demo.topic   +-----+
|                |
+----------------+
```

Use sub topics like so:
```
+----------------+
|   Brewer 1     |
| demo.topic.b1  +-----+
|                |     |    +-----------------+
+----------------+     |    |     Patron      |
                       +---->  demo.topic.**  |
+----------------+     |    |                 |
|   Brewer 2     |     |    +-----------------+
| demo.topic.b2  +-----+
|                |
+----------------+
```
