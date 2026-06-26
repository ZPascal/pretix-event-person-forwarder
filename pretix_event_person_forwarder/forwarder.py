import json
import logging

from .api import Api
from .model import APIModel, APIEndpoints, RequestsMethods
from .orders import Orders
from .questions import Questions


class Forwarder:
    """The class includes all necessary methods to forward event persons between Pretix instances

        Args:
            source_api_model (APIModel): Inject an API model object for the source Pretix instance
            dest_api_model (APIModel): Inject an API model object for the destination Pretix instance
            rules (dict): A dictionary defining the field mapping rules between source and destination
            mode (str): The forwarding mode; must be 'skip' to skip existing attendees or 'update' to patch them

        Attributes:
            source_api_model (APIModel): This is where we store the source_api_model
            dest_api_model (APIModel): This is where we store the dest_api_model
            rules (dict): This is where we store the rules
            mode (str): This is where we store the mode
        """

    def __init__(
        self,
        source_api_model: APIModel,
        dest_api_model: APIModel,
        rules: dict,
        mode: str,
    ):
        if mode not in ("skip", "update"):
            logging.error(f"Invalid mode '{mode}'. Must be 'skip' or 'update'.")
            raise ValueError(f"Invalid mode '{mode}'. Must be 'skip' or 'update'.")
        self.source_api_model = source_api_model
        self.dest_api_model = dest_api_model
        self.rules = rules
        self.mode = mode

    def forward_event_persons(
        self,
        source_organizer: str,
        source_event: str,
        dest_organizer: str,
        dest_event: str,
    ) -> None:
        """The method includes a functionality to forward event persons from a source event to a destination event

        Args:
            source_organizer (str): Specify the organizer slug of the source Pretix instance
            source_event (str): Specify the event slug on the source Pretix instance
            dest_organizer (str): Specify the organizer slug of the destination Pretix instance
            dest_event (str): Specify the event slug on the destination Pretix instance

        Raises:
            ValueError: Raised when a destination question ID defined in the rules is not found in the destination event
            ValueError: Raised when an invalid mode is provided during initialisation

        Returns:
            None
        """

        dest_question_ids = {
            q["id"]
            for q in Questions(self.dest_api_model).get_all_event_questions(
                dest_organizer, dest_event
            )
        }
        for mapping in self.rules.get("fields", {}).get("questions", []):
            if mapping["dest_id"] not in dest_question_ids:
                logging.error(f"Destination question ID {mapping['dest_id']} not found in event '{dest_event}'.")
                raise ValueError(
                    f"Destination question ID {mapping['dest_id']} not found in event '{dest_event}'."
                )

        source_orders = Orders(self.source_api_model).get_event_orders(
            source_organizer, source_event
        )
        dest_orders = Orders(self.dest_api_model).get_event_orders(
            dest_organizer, dest_event
        )

        dest_by_email: dict = {}
        for order in dest_orders:
            for position in order.get("positions", []):
                email = position.get("attendee_email")
                if email:
                    if email in dest_by_email:
                        logging.warning(f"Duplicate email in destination orders: {email}. Using latest position.")
                    dest_by_email[email] = {"order_code": order["code"], "position_id": position["id"]}

        question_map = {
            m["source_id"]: m["dest_id"]
            for m in self.rules.get("fields", {}).get("questions", [])
        }

        for order in source_orders:
            for position in order.get("positions", []):
                self._process_position(
                    position, dest_organizer, dest_event, dest_by_email, question_map
                )

    def _process_position(
        self,
        position: dict,
        dest_organizer: str,
        dest_event: str,
        dest_by_email: dict,
        question_map: dict,
    ) -> None:
        email = position.get("attendee_email")
        mapped_answers = [
            {"question": question_map[a["question"]], "answer": a["answer"]}
            for a in position.get("answers", [])
            if a["question"] in question_map
        ]

        if email and email in dest_by_email:
            if self.mode == "skip":
                logging.info(f"Skipping existing attendee: {email}")
                return
            ref = dest_by_email[email]
            payload = {
                "attendee_name": position.get("attendee_name"),
                "attendee_email": email,
                "answers": mapped_answers,
            }
            Api(self.dest_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{dest_organizer}/{APIEndpoints.EVENTS.value}"
                f"/{dest_event}/{APIEndpoints.ORDERS.value}/{ref['order_code']}"
                f"/positions/{ref['position_id']}/",
                method=RequestsMethods.PATCH,
                json_complete=json.dumps(payload),
            )
            logging.info(f"Updated attendee: {email}")
        else:
            payload = {
                "positions": [
                    {
                        "attendee_name": position.get("attendee_name"),
                        "attendee_email": email,
                        "answers": mapped_answers,
                    }
                ],
                "email": email or "",
                "locale": "en",
                "sales_channel": "web",
                "payment_provider": "manual",
            }
            Api(self.dest_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{dest_organizer}/{APIEndpoints.EVENTS.value}"
                f"/{dest_event}/{APIEndpoints.ORDERS.value}/",
                method=RequestsMethods.POST,
                json_complete=json.dumps(payload),
            )
            logging.info(f"Created attendee: {email}")
