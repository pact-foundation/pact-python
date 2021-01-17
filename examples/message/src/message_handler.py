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
    def __init__(self, message):
        self.message = message
        self.verify_content()

    def check_message_exist(self):
        return "Message exists" if bool(self.message) else "Message does NOT exist"

    def verify_content(self):
        if self.message[0]['metaData'].get('Content-Type') != 'application/json':
            raise CustomError("Not correct Content-type")
