import uuid
import os
from google.cloud.dialogflowcx_v3beta1.services.agents import AgentsClient
from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
from google.cloud.dialogflowcx_v3beta1.types import session
from google.protobuf.json_format import MessageToDict

import logging
from user_session import UserSession

logging.basicConfig(format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_cred.json"


class SetupGDF:
    """
    SetupGDF is responsible for setting up the environment for communication with
    Google Dialog Flow CX.
    """

    def __init__(self, user_id=None, custom_session_id=None) -> None:
        logger.info("Setup GDF Initiated ... ")
        self.prepare_agent()
        self.prepare_session(user_id)
        self.prepare_session_client()
        self.language_code = "en-us"

    def prepare_agent(self):
        logger.info("Preparing Agent Initiated ... ")
        self.project_id = os.environ["GDF_PROJECT_ID"]
        self.location_id = os.environ["GDF_LOCATION"]
        self.agent_id = os.environ["AGENT_ID"]
        self.agent = f"projects/{self.project_id}/locations/{self.location_id}/agents/{self.agent_id}"
        logger.info("Preparing Agent Completed!")

    def prepare_session(self, user_id):
        """
        Preparing session for the user
            Fetching the already stored Session ID
            If not => Create new Session ID
            TODO: For scale and production - Use Redis or similar alternatives
            for faster and efficient storage
        """
        logger.info("Preparing Session Initiated ... ")
        self.user_session_obj = UserSession()
        if self.user_session_obj.is_session(user_id=user_id):
            self.session_id = self.user_session_obj.get_session_id(user_id=user_id)
            logger.info(f"Session already exist as session ID - {self.session_id}")
        else:
            self.user_session_obj.create_session(
                user_id=user_id, session_id=str(uuid.uuid4())
            )
            self.session_id = self.user_session_obj.get_session_id()
            logger.info(f"Session created as  - {self.session_id}")

        logger.info("Preparing Session Completed!")

    def prepare_session_client(self):
        """
        Returns the result of detect intent with texts as inputs.

        Using the same `session_id` between requests allows continuation
        of the conversation.
        """

        logger.info("Preparing Session Client Initiated ... ")
        self.session_path = f"{self.agent}/sessions/{self.session_id}"
        client_options = None
        agent_components = AgentsClient.parse_agent_path(self.agent)
        location_id = agent_components["location"]
        if location_id != "global":
            api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
            print(f"API Endpoint: {api_endpoint}\n")
            client_options = {"api_endpoint": api_endpoint}
        self.session_client = SessionsClient(client_options=client_options)
        logger.info("Preparing Session Client Completed!")

    def prepare_gdf_request(self, text):
        logger.info("Preparing GDF Request ... ")
        text_input = session.TextInput(text=text)
        query_input = session.QueryInput(
            text=text_input, language_code=self.language_code
        )
        request = session.DetectIntentRequest(
            session=self.session_path, query_input=query_input
        )
        logger.info("GDF Response recieved!")
        return request

    @classmethod
    def process_response(cls, response_json):
        """
        Processing response from GDF to be able to injected to usable format
        """
        response_messages = []
        option_list = []
        rich_content_type = None
        try:
            for msg in response_json["queryResult"]["responseMessages"]:
                if "text" in msg:
                    response_messages.extend(msg["text"]["text"])
                elif "payload" in msg:
                    rich_content = msg["payload"]["richContent"][0][0]
                    rich_content_type = rich_content["type"]
                    if rich_content_type == "chips":
                        for option in rich_content["options"]:
                            option_list.append(option["text"])
            logger.info("Processing of GDF Response done!")
        except Exception as e:
            logger.error(f"Processing of GDF Response Failed due to {e}!")

        return response_messages, option_list, rich_content_type

    def detect_intent_texts_utils(self, texts):
        """
        Get the response from GDF Engine
        """

        for text in texts:
            request = self.prepare_gdf_request(text)
            response = self.session_client.detect_intent(request=request)
            response_json = MessageToDict(response._pb)

            return self.process_response(response_json=response_json)

    def detect_intent_texts(self, texts):
        """
        Interface to get the response from GDF Engine
        """
        logger.info("Fetching response from GDF Engine ... ")
        response = self.detect_intent_texts_utils(texts)
        logger.info("Response from GDF Engine recieved! - {}".format(response))
        return response
