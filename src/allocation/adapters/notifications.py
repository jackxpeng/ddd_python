import abc
import smtplib
from allocation import config

class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, destination, message):
        raise NotImplementedError

email_config = config.get_email_host_and_port()
DEFAULT_HOST: str = str(email_config["host"])
DEFAULT_PORT: int = int(email_config["port"])

class EmailNotifications(AbstractNotifications):
    def __init__(self, smtp_host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.smtp_host = smtp_host
        self.port = port

    def send(self, destination, message):
        msg = f"Subject: allocation service notification\n{message}"
        server = smtplib.SMTP(self.smtp_host, port=self.port)
        server.sendmail(
            from_addr="allocations@example.com",
            to_addrs=[destination],
            msg=msg,
        )
        server.quit()