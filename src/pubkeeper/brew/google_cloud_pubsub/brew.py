from collections import defaultdict
from copy import copy
from os import getenv
from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1
from pubkeeper.brew.base import Brew
from . import BrewSettings


class GoogleCloudPubSubBrew(Brew):

    name = 'google_cloud_pubsub'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Can do any basic init-ing, or opening known connections
        self._gcp_project = None
        # if acting as a brewer, and/or patron, you may need to
        # open sockets, or prep them for use within tornado IOLoop
        self._publisher = None
        self._subscriber = None
        # A dictionary mapping patron IDs to counts of subscriptions to
        # topics. This way we know when to tear down a subscription
        self._topic_subscribers = defaultdict(lambda: defaultdict(int))

    @classmethod
    def get_settings(cls):
        return BrewSettings

    def configure(self, context):
        self._logger.info("Configuring")
        self._gcp_project = context.get('gcp_project')
        GCP_ENV_VAR = 'GOOGLE_APPLICATION_CREDENTIALS'
        service_account_file = context.get('service_account_file')
        if not service_account_file and not getenv(GCP_ENV_VAR):
            self._logger.warning(
                "No service account specified and {} env var is not set. "
                "You may not be able to authenticate to GCP".format(
                    GCP_ENV_VAR))

    def create_brewer(self, brewer):
        if self._publisher is None:
            self._publisher = pubsub_v1.PublisherClient()
        try:
            self._logger.info("Creating GCP Topic for {}".format(brewer.topic))
            self._publisher.create_topic(
                self._publisher.topic_path(self._gcp_project, brewer.topic))
        except AlreadyExists:
            # Ignore errors if the topic already exists
            self._logger.debug(
                "GCP Topic {} already exists".format(brewer.topic))

    def create_patron(self, patron):
        if self._subscriber is None:
            self._subscriber = pubsub_v1.SubscriberClient()

    def destroy_patron(self, patron):
        # Destroy any resources that were created for the specific patron
        self._logger.info("Down patron")
        subscriptions = self._topic_subscribers[patron.patron_id]
        for topic in copy(subscriptions):
            self.__remove_subscription(patron.patron_id, topic)

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        try:
            self.__create_subscription(patron_id, topic)
        except Exception:
            self._logger.exception(
                "Couldn't create subscription for "
                "patron {}, topic {}".format(patron_id, topic))
            return

        def sub_callback(message):
            message.ack()
            callback(brewer_id, message.data)

        sub_path, _ = self.__get_patron_subscriber_details(patron_id, topic)
        self._subscriber.subscribe(sub_path, callback=sub_callback)

    def stop_patron(self, patron_id, topic, brewer_id):
        self.__remove_subscription(patron_id, topic)

    def __create_subscription(self, patron_id, topic):
        """ Ensure that we have a subscription created in GCP for a topic """
        self._topic_subscribers[patron_id][topic] += 1
        if self._topic_subscribers[patron_id][topic] == 1:
            self._logger.info("Creating a new GCP subscription resource for "
                              "patron {}, topic {}".format(patron_id, topic))
            # We just created this subscriber, let's make the resource
            sub_path, topic_path = self.__get_patron_subscriber_details(
                patron_id, topic)
            self._subscriber.create_subscription(sub_path, topic_path)

    def __remove_subscription(self, patron_id, topic):
        """ Decrement the count of subscriptions and remove if we're done """
        self._topic_subscribers[patron_id][topic] -= 1
        if self._topic_subscribers[patron_id][topic] <= 0:
            # We just removed the last subscriber, delete the resource
            self._logger.info("Deleting GCP subscription resource for "
                              "patron {}, topic {}".format(patron_id, topic))
            sub_path, _ = self.__get_patron_subscriber_details(
                patron_id, topic)
            self._subscriber.delete_subscription(sub_path)
            # Remove it from the list of subscribers too
            del self._topic_subscribers[patron_id][topic]

    def __get_patron_subscriber_details(self, patron_id, topic):
        """ Return a tuple of subscription path and topic path """
        return (
            self._subscriber.subscription_path(
                self._gcp_project, "sub.{}.{}".format(patron_id, topic)),
            self._subscriber.topic_path(self._gcp_project, topic))

    def brew(self, brewer_id, topic, data, patrons):
        self._publisher.publish(
            self._publisher.topic_path(self._gcp_project, topic),
            data)
