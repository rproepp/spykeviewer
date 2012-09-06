from spykeutils.plugin.data_provider_neo import NeoDataProvider

class NeoViewerProvider(NeoDataProvider):
    def __init__(self, viewer, name='__current__'):
        super(NeoViewerProvider, self).__init__(name, viewer.progress)
        self.viewer = viewer

    def blocks(self):
        """ Return a list of selected Block objects
        """
        return self.viewer.neo_blocks()

    def segments(self):
        """ Return a list of selected Segment objects
        """
        return self.viewer.neo_segments()

    def recording_channel_groups(self):
        """ Return a list of selected
        """
        return self.viewer.neo_channel_groups()

    def recording_channels(self):
        """ Return a list of selected recording channel indices
        """
        return self.viewer.neo_channels()

    def units(self):
        """ Return a list of selected Unit objects
        """
        return self.viewer.neo_units()

    def data_dict(self):
        """ Return a dictionary with all information to serialize the object
        """
        data = NeoViewerProvider._get_data_from_viewer(self.viewer)
        data['name'] = self.name
        return data