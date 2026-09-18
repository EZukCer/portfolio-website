import json
import uuid
import re
from datetime import datetime, timezone

import boto3

VALIDATION_LIMITS = {
    "firstName": 25,
    "lastName": 25,
    "email": 50,
    "reason": 20,
    "message": 500,
}

dynamodb = boto3.resource("dynamodb", region_name="eu-west-2")
table = dynamodb.Table("portfolio-website-enquiries")

ses = boto3.client("ses", region_name="eu-west-2")


def response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": message
        })
    }


def lambda_handler(event, context):
    try:
        body = event.get("body")

        if not body:
            return response(400, "Request body is required")

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return response(400, "Invalid JSON")

        if data.get("website"):
            return response(400, "Invalid request")

        required_fields = [
            "firstName",
            "lastName",
            "email",
            "reason",
            "message"
        ]

        for field in required_fields:
            if not isinstance(data.get(field), str) or not data[field].strip():
                return response(400, f"{field} is required")

        first_name = data["firstName"].strip()
        last_name = data["lastName"].strip()
        email = data["email"].strip()
        reason = data["reason"].strip()
        message = data["message"].strip()

        if len(message) > VALIDATION_LIMITS["message"]:
            return response(
                400,
                "Message must be 500 characters or fewer"
            )

        if len(first_name) > VALIDATION_LIMITS["firstName"]:
            return response(400, "First name is too long")

        if len(last_name) > VALIDATION_LIMITS["lastName"]:
            return response(400, "Last name is too long")

        if len(email) > VALIDATION_LIMITS["email"]:
            return response(400, "Email address is too long")

        if len(reason) > VALIDATION_LIMITS["reason"]:
            return response(400, "Reason is too long")

        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(email_pattern, email):
            return response(400, "Invalid email address")

        enquiry = {
            "id": str(uuid.uuid4()),
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "reason": reason,
            "message": message,
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        table.put_item(Item=enquiry)

        print(f"Enquiry saved successfully: {enquiry['id']}")

        ses.send_email(
            Source="Erik Z <erik@erikthedev.com>",
            Destination={
                "ToAddresses": [
                    "erik@erikthedev.com"
                ]
            },
            ReplyToAddresses=[
                email
            ],
            Message={
                "Subject": {
                    "Data": f"AWS Outreach PP: [{reason}] {first_name} {last_name}",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": (
                            f"New contact enquiry\n\n"
                            f"Name: {first_name} {last_name}\n"
                            f"Email: {email}\n"
                            f"Reason: {reason}\n\n"
                            f"Message:\n{message}\n\n"
                            f"Received: {enquiry['createdAt']}\n"
                            f"Enquiry ID: {enquiry['id']}"
                        ),
                        "Charset": "UTF-8"
                    }
                }
            }
        )

        print(f"Notification email sent for enquiry: {enquiry['id']}")

        ses.send_email(
            Source="Erik Z <erik@erikthedev.com>",
            Destination={
                "ToAddresses": [
                    email
                ]
            },
            Message={
                "Subject": {
                    "Data": "Thanks for reaching out",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": (
                            f"Hi {first_name},\n\n"
                            f"Thanks for reaching out through my website.\n\n"
                            f"I've received your message and will get back to you "
                            f"within 2–4 days.\n\n"
                            f"Best,\n"
                            f"Erik\n"
                        ),
                        "Charset": "UTF-8"
                    }
                }
            }
        )

        print(f"Confirmation email sent to visitor for enquiry: {enquiry['id']}")

        return response(200, "Enquiry received successfully")

    except Exception as error:
        print(f"Error processing enquiry: {error}")
        return response(500, "Internal server error")