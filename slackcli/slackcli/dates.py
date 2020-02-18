from slackcli.conversations import Conversation


class Date:
    """Class representing a specific date."""
    def __init__(self, export, files, date, convo_type):
        self.export = export
        self.files = files
        self.date = date
        self.convo_type = convo_type
        self.convos = None
        self.set_convos()
        self.convos.sort(key=lambda convo: convo.time)

    def set_convos(self):
        """Set convos attribute with list of Conversation objects for that instance's date."""
        self.convos = [Conversation(self.export.open_json_file(file[0]), self, file)
                       for file in self.files
                       if self.date == file[1]]

