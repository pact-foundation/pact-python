class CustomError(Exception):
    def __init__(self, *args):
        if args:
            self.topic = args[0]
        else:
            self.topic = None

    def __str__(self):
        if self.topic:
            return 'Custom Error:, {0}'.format(self.topic)

class MessageHandler(object):
    def __init__(self, event):
        self.pass_event(event)

    @staticmethod
    def pass_event(event):
        if event.get('documentType') != 'microsoft-word':
            raise CustomError("Not correct document type")
