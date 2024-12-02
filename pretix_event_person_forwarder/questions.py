import logging

from .model import APIModel, APIEndpoints
from .api import Api

class Questions:
    """The class includes all necessary methods to access the Pretix questions API endpoints

        Args:
            pretix_api_model (APIModel): Inject a Grafana API model object that includes all necessary values and information

        Attributes:
            pretix_api_model (APIModel): This is where we store the pretix_api_model
        """

    def __init__(self, pretix_api_model: APIModel):
        self.pretix_api_model = pretix_api_model

    def get_event_question(self,
            organizer: str,
            event_name: str,
            question_id: int,
    ) -> dict:
        """The method includes a functionality to get a question of the specified event

        Args:
            organizer (str): Specify the organizer of the events
            event_name (str): Specify the event name
            question_id (int): Specify the question id

        Raises:
            ValueError: Missed specifying a necessary value
            Exception: Unspecified error by executing the API call

        Returns:
            api_call (list): Returns a list of the events
        """

        if len(organizer) != 0 and len(event_name) != 0 and question_id != 0:
            api_call: dict = Api(self.pretix_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{organizer}/{APIEndpoints.EVENTS.value}/{event_name}/{APIEndpoints.QUESTIONS.value}/{question_id}",
            )

            if len(api_call) == 0 or api_call.get("id") == 0:
                logging.error(f"Check the error: {api_call}.")
                raise Exception
            else:
                return api_call
        else:
            logging.error(
                "There is no organizer, event_name or question_id defined."
            )
            raise ValueError

    def get_all_event_questions(
            self,
            organizer: str,
            event_name: str,
    ) -> list:
        """The method includes a functionality to get all questions of the specified event

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
                f"{APIEndpoints.ORGANIZERS.value}/{organizer}/{APIEndpoints.EVENTS.value}/{event_name}/{APIEndpoints.QUESTIONS.value}",
            )

            if (api_call.get("counts") is not None and api_call.get("counts") >= 0 and
                    api_call.get("results")[0].get("id") is None):
                logging.error(f"Check the error: {api_call}.")
                raise Exception
            else:
                return api_call.get("results")
        else:
            logging.error(
                "There is no organizer or event_name defined."
            )
            raise ValueError