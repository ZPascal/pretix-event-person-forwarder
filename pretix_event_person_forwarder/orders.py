import logging

from .model import APIModel, APIEndpoints
from .api import Api

class Orders:
    """The class includes all necessary methods to access the Pretix events API endpoints

        Args:
            pretix_api_model (APIModel): Inject a Grafana API model object that includes all necessary values and information

        Attributes:
            pretix_api_model (APIModel): This is where we store the pretix_api_model
        """

    def __init__(self, pretix_api_model: APIModel):
        self.pretix_api_model = pretix_api_model

    def get_event_orders(
            self,
            organizer: str,
            event_name: str,
    ) -> list:
        """The method includes a functionality to get all orders of the specified event

        Args:
            organizer (str): Specify the organizer of the events
            event_name (str): Specify the event name

        Raises:
            ValueError: Missed specifying a necessary value
            Exception: Unspecified error by executing the API call

        Returns:
            api_call (list): Returns a list of the events
        """

        if len(organizer) != 0 and len(event_name) != 0:
            api_call: dict = Api(self.pretix_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{organizer}/{APIEndpoints.EVENTS.value}/{event_name}/{APIEndpoints.ORDERS.value}",
            )

            if (api_call.get("counts") is not None and api_call.get("counts") >= 0 and
                    api_call.get("results")[0].get("event") is None):
                logging.error(f"Check the error: {api_call}.")
                raise Exception
            else:
                return api_call.get("results")
        else:
            logging.error(
                "There is no organizer or event_name defined."
            )
            raise ValueError

    def get_all_orders(
            self,
            organizer: str,
    ) -> list:
        """The method includes a functionality to get all orders of the specified organizer

        Args:
            organizer (str): Specify the organizer of the events

        Raises:
            ValueError: Missed specifying a necessary value
            Exception: Unspecified error by executing the API call

        Returns:
            api_call (list): Returns a list of the events
        """

        if len(organizer) != 0:
            api_call: dict = Api(self.pretix_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{organizer}/{APIEndpoints.ORDERS.value}",
            )

            if (api_call.get("counts") is not None and api_call.get("counts") >= 0 and
                    api_call.get("results")[0].get("event") is None):
                logging.error(f"Check the error: {api_call}.")
                raise Exception
            else:
                return api_call.get("results")
        else:
            logging.error(
                "There is no organizer defined."
            )
            raise ValueError