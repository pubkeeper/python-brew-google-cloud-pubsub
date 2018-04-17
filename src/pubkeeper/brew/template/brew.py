from pubkeeper.brew.base import Brew
from pubkeeper.brew.template import TemplateSettings


class TemplateBrew(Brew):
    name = 'template'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Can do any basic init-ing, or opening known connections
        # if acting as a brewer, and/or patron, you may need to
        # open sockets, or prep them for use within tornado IOLoop

    @classmethod
    def get_settings(cls):
        return TemplateSettings

    def configure(self, context):
        pass

    def start(self):
        # For some brewers you may open a patron socket for brewers to
        # send data to, this will be a coroutine that will await data
        # from potential sets of brewers
        pass

    def stop(self):
        # Disconnect any open connections you may have created
        pass

    def create_brewer(self, brewer):
        # If per-brewer resources are necessary, this method can allocate and
        # store the resource for the specified topic.  The return value of this
        # method _must_ be a dictionary, that will be included with the brewers
        # registration
        pass

    def destroy_brewer(self, brewer):
        # Destroy any resources that were created for the specific brewer
        pass

    def create_patron(self, patron):
        # If per-patron resources are necessary, this method can allocate and
        # store the resource for the specified topic.  The return value of this
        # method _must_ be a dictionary, that will be included with the patrons
        # registration
        pass

    def destroy_patron(self, patron):
        # Destroy any resources that were created for the specific patron
        pass

    def start_brewer(self, brewer_id, topic, patron_id, patron):
        # The specified patron has joined the network, and will be consuming
        # this brews resouce.  If you need to, any specific handling can take
        # place here.
        pass

    def stop_brewer(self, brewer_id, topic, patron_id):
        # The specified patron has left the network.  If the brewer keeps
        # track or cares about the connected patron
        pass

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        # Start patronizing the given brewer.  Provided with all necessary
        # configuration for this brewer if needed to properly connect to
        # the resource.  Any received data should be passed to the callback
        pass

    def stop_patron(self, patron_id, topic, brewer_id):
        # Stop patronizing the specified brewer.  Destory any resources that
        # may have been necessary to get the data
        pass

    def brew(self, brewer_id, topic, data, patrons):
        # Handle the sending of data for the brewer on the topic.  The patrons
        # given are in the event patron data is necessary for the transporation.
        pass
