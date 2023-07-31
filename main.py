from flask import request, Response, make_response
import os
from gdf_setup import SetupGDF
import logging
from app import app
from whatsapp_handler import WhatsAppHandler
from user_session import UserSession

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.route("/recieve_from_whatsapp", methods=["POST", "GET"])
def get_message_from_cloud_meta_api():
    # Data flow is certain so there shoud not be any issue rather flask throw traceback
    # we want errors to be thrown

    if request.method == "POST":
        data = request.json

        logger.info("Recieved Whatsapp message from user.")
        # 1. Process the response from event
        phone_number, message = WhatsAppHandler.process_request(data)

        # 2. Get Response Message from Google DialogFlow CX
        if message:
            (
                res_msg,
                option_list,
                rich_content_type,
            ) = WhatsAppHandler.prepare_response_gdf(phone_number, message)

            # 3. Send it back to user
            if res_msg and option_list and rich_content_type:
                res = WhatsAppHandler.sendWhatsAppMessageUtils(
                    phoneNumber=phone_number,
                    message=res_msg,
                    option_list=option_list,
                    rich_content_type=rich_content_type,
                )
                logger.info("Successfully sent the response from GDF!")
                return make_response({"data": res_msg}, 200)
            else:
                logger.error("Error : Could not process message")
                return make_response({"data": "Error"}, 400)
        else:
            logger.error("Error : Could not process message")
            return make_response({"data": "Error"}, 400)

    if request.method == "GET":
        """
        Verification of Token : Cloud Meta Platform
        """
        hub_mode = request.args.get("hub.mode")
        webhook_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if hub_mode == "subscribe" and webhook_token == os.environ["VERIFY_TOKEN"]:
            return Response({challenge}, status=200)
        else:
            return Response({"error"}, status=403)

