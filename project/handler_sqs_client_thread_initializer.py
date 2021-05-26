import threading


class HandlerSqsClientThreadInitializer():

    def __init__(self, handler_sqs_client):
        self.handler_sqs_client = handler_sqs_client
        thread = threading.Thread(target=self.receive_message)
        thread.setDaemon(True)
        thread.start()

    def receive_message(self):
        self.handler_sqs_client.receive_message()
