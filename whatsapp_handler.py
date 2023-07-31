import os
from app import app
import requests
import json
from gdf_setup import SetupGDF
import logging

logger = logging.getLogger(__name__)

# Using Builder Design Pattern


class WhatsAppHandler:

    """
    Whatsapp Utility Methods - To process the requests and response

    """

    @classmethod
    def build_rich_content(cls, option_list, rich_content_type):
        """
        Handling of Rich Content :
            List
            Buttons
            Plain Text
        """
        rc_list = []

        for option in option_list:
            rc_list.append(
                {"type": "reply", "reply": {"id": option + "-id", "title": option}}
            )

        return rc_list

    @classmethod
    def get_send_message_url(cls):
        """
        Cloud Meta API - for sending message to User
        TODO: Can change later to on-premise
        """
        url = "https://graph.facebook.com/v17.0/115622904949472/messages"
        return url

    @classmethod
    def get_header(cls):
        """
        Preparing Header for the Request
        """
        bearer_token = os.environ["BEARER"]
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }
        return headers

    @classmethod
    def get_response(cls, payload):
        """
        Sending response to user through Cloud Meta API
        """
        logger.info("Sending message to user ...")
        response = requests.request(
            "POST", cls.get_send_message_url(), headers=cls.get_header(), data=payload
        )
        logger.info(
            "Sending message to user finished with response - {}!".format(response)
        )
        return response

    @classmethod
    def prepare_payload(cls, option_list, rich_content_type, phoneNumber, message):
        """
        Preparing Payload based on GDF response
            Rich Content
        """
        if option_list:
            button_formatted_list = WhatsAppHandler.build_rich_content(
                option_list, rich_content_type
            )
            payload = json.dumps(
                {
                    "messaging_product": "whatsapp",
                    "to": phoneNumber,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": message},
                        "action": {"buttons": button_formatted_list[:3]},
                    },
                }
            )

        else:
            payload = json.dumps(
                {
                    "messaging_product": "whatsapp",
                    "to": phoneNumber,
                    "type": "text",
                    "text": {"body": message},
                }
            )
        return payload

    @classmethod
    def sendWhatsAppMessageUtils(
        cls,
        phoneNumber,
        message="Test Message",
        option_list=None,
        rich_content_type=None,
    ):
        """
        Interface to send response back to user
        """
        logger.info("Sending response from GDF to whatsapp user intiated ... ")
        payload = cls.prepare_payload(
            option_list, rich_content_type, phoneNumber, message
        )
        response = cls.get_response(payload)
        logger.info("Sending response from GDF to whatsapp user completed")
        return response

    @classmethod
    def prepare_response_gdf(cls, user_id, message):
        """
        Interface to send request and prepare response from GDF
        """
        logger.info("Fetching response from GDF Initiated ... ")
        gdf_obj = SetupGDF(user_id)

        (
            res_msg,
            option_list,
            rich_content_type,
        ) = gdf_obj.detect_intent_texts([message])

        # 3. Package messages
        res_msg = " ".join(res_msg)
        return (res_msg, option_list, rich_content_type)

    @classmethod
    def process_request(cls, data):
        """
        - Processing the response coming from cloud Meta on CallBack URL
        - The function requires to throw error if any, as it's a flow with
            single possibility. So if it fails, it should be throwing error

        """

        logger.info("Processing of whatsapp response initiated ... ")

        if "object" in data and "entry" in data:
            if data["object"] == "whatsapp_business_account":
                try:
                    for entry in data["entry"]:
                        
                            message_obj = entry["changes"][0]["value"]["messages"][0]
                            phoneNumber = message_obj["from"]

                            # Processing for interactive and plain text
                            if message_obj["type"] == "text":
                                message = message_obj["text"]["body"]
                            elif message_obj["type"] == "interactive":
                                if message_obj["interactive"]["type"] == "button_reply":
                                    message = message_obj["interactive"]["button_reply"][
                                        "title"
                                    ]
                            logger.info(f"Processing of whatsapp response completed ... {phoneNumber}, {message} ")
                            return phoneNumber, message
                except Exception as e:
                    logger.error(f"Please check the response json! - {e} ")
                    return None, None
            else:
                logger.warning("Please check the response json! - failed data[object] == whatsapp_business_account")
        else:
            logger.warning("Please check the response json!")
        return None, None
