import logging

from .model import APIModel, APIEndpoints
from .api import Api

class Events:
    """The class includes all necessary methods to access the Pretix events API endpoints

        Args:
            pretix_api_model (APIModel): Inject a Grafana API model object that includes all necessary values and information

        Attributes:
            pretix_api_model (APIModel): This is where we store the pretix_api_model
        """

    def __init__(self, pretix_api_model: APIModel):
        self.pretix_api_model = pretix_api_model

    def get_events(
            self,
            organizer: str,
    ) -> list:
        """The method includes a functionality to get all events of the organizer

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
                f"{APIEndpoints.ORGANIZERS.value}/{organizer}/{APIEndpoints.EVENTS.value}",
            )

            if (api_call.get("counts") is not None and api_call.get("counts") >= 0 and
                    api_call.get("results")[0].get("name") is None):
                logging.error(f"Check the error: {api_call}.")
                raise Exception
            else:
                return api_call.get("results")
        else:
            logging.error(
                "There is no organizer defined."
            )
            raise ValueError

    def get_event(
            self,
            organizer: str,
            event_name: str,
    ) -> dict:
        """The method includes a functionality to get a event of the organizer

        Args:
            organizer (str): Specify the organizer of the events
            event_name (str): Specify the event name

        Raises:
            ValueError: Missed specifying a necessary value
            Exception: Unspecified error by executing the API call

        Returns:
            api_call (dict): Returns the event
        """

        if len(organizer) != 0 and len(event_name) != 0:
            api_call: dict = Api(self.pretix_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{organizer}/{APIEndpoints.EVENTS.value}",
            )

            if api_call.get("name") is not None and len(api_call.get("name")) != 0:
                logging.error(f"Check the error: {api_call}.")
                raise Exception
            else:
                return api_call
        else:
            logging.error(
                "There is no organizer or event_name defined."
            )
            raise ValueError
