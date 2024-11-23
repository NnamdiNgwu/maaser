from abc import ABC, abstractmethod
from models.message import Message
from utils.zmq_utils import create_subscriber, create_req_socket


class BaseService(ABC):
    def __init__(self, name, sub_port, sub_topics, coordinator_port):
        """
        Initializes a BaseService instance with the provided parameters.

        Parameters:
        name (str): The name of the service.
        sub_port (int): The port number for the subscriber socket to listen for incoming messages.
        sub_topics (list): A list of topics to subscribe to.
        coordinator_port (int): The port number for the request socket to communicate with the coordinator.

        Returns:
        None
        """
        self.name = name
        self.sub_socket = create_subscriber(sub_port, sub_topics)
        self.req_socket = create_req_socket(coordinator_port)


    @abstractmethod
    def process_message(self, message: Message):
        pass
    @abstractmethod
    def process_message(self, message: Message):
        """
        This method is intended to be overridden by subclasses to process incoming messages.

        Parameters:
        message (Message): The incoming message to be processed. The message is an instance of the Message class, which contains sender, receiver, action, and data attributes.

        Returns:
        None
        """
        pass

    def run(self):
        """
        This function continuously listens for incoming messages on the subscribed topics.
        When a message is received, it is parsed and passed to the process_message method.

        Parameters:
        None

        Returns:
        None
        """
        while True:
            topic = self.sub_socket.recv_string()
            message = Message.parse_raw(self.sub_socket.recv_json())
            self.process_message(message)


    def send_message(self, receiver, action, data):
        """
        Sends a message to a specified receiver with the given action and data.
        The message is then sent over a request socket to the coordinator.
        The response from the coordinator is returned.

        Parameters:
        receiver (str): The name of the receiver service.
        action (str): The action to be performed by the receiver service.
        data (dict): The data to be included in the message.

        Returns:
        dict: The response received from the coordinator.
        """
        message = Message(sender=self.name, receiver=receiver, action=action, data=data)
        self.req_socket.send_json(message.dict())
        response = self.req_socket.recv_json()
        return response