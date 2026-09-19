import json
import sys
from pathlib import Path
from unittest.mock import Mock
from bs4 import BeautifulSoup

import pytest


# Allow the test file to import lambda_function.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import lambda_function


def valid_event():
    return {
        "body": json.dumps({
            "firstName": "Erik",
            "lastName": "Zukov",
            "email": "visitor@example.com",
            "reason": "Project",
            "message": "I'd like to discuss a project.",
            "website": ""
        })
    }


@pytest.fixture
def mocked_aws(monkeypatch):
    mock_table = Mock()
    mock_ses = Mock()

    monkeypatch.setattr(lambda_function, "table", mock_table)
    monkeypatch.setattr(lambda_function, "ses", mock_ses)

    return mock_table, mock_ses


def get_response_body(response):
    return json.loads(response["body"])


# ---------------------------------------------------------
# Basic request validation
# ---------------------------------------------------------


def test_valid_enquiry(mocked_aws):
    table, ses = mocked_aws

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 200
    assert get_response_body(result)["message"] == (
        "Enquiry received successfully"
    )

    table.put_item.assert_called_once()
    assert ses.send_email.call_count == 2


def test_missing_body(mocked_aws):
    table, ses = mocked_aws

    result = lambda_function.lambda_handler({}, None)

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Request body is required"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_empty_body(mocked_aws):
    table, ses = mocked_aws

    result = lambda_function.lambda_handler(
        {"body": ""},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Request body is required"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_invalid_json(mocked_aws):
    table, ses = mocked_aws

    event = {
        "body": "this is not valid JSON"
    }

    result = lambda_function.lambda_handler(event, None)

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == "Invalid JSON"

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


# ---------------------------------------------------------
# Required fields
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "field",
    [
        "firstName",
        "lastName",
        "email",
        "reason",
        "message",
    ],
)
def test_missing_required_field(mocked_aws, field):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    del event_data[field]

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        f"{field} is required"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


@pytest.mark.parametrize(
    "field",
    [
        "firstName",
        "lastName",
        "email",
        "reason",
        "message",
    ],
)
def test_empty_required_field(mocked_aws, field):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data[field] = ""

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        f"{field} is required"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


@pytest.mark.parametrize(
    "field",
    [
        "firstName",
        "lastName",
        "email",
        "reason",
        "message",
    ],
)
def test_whitespace_required_field(mocked_aws, field):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data[field] = "   "

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        f"{field} is required"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


# ---------------------------------------------------------
# Honeypot
# ---------------------------------------------------------


def test_empty_honeypot_is_accepted(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["website"] = ""

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200
    table.put_item.assert_called_once()
    assert ses.send_email.call_count == 2


def test_populated_honeypot_is_rejected(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["website"] = "https://spam.example"

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == "Invalid request"

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


# ---------------------------------------------------------
# Length validation
# ---------------------------------------------------------


def test_message_too_long(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["message"] = "a" * 501

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Message must be 500 characters or fewer"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_message_exactly_500_characters(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["message"] = "a" * 500

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200
    table.put_item.assert_called_once()
    assert ses.send_email.call_count == 2


def test_first_name_too_long(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["firstName"] = "a" * 26

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "First name is too long"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_first_name_exactly_25_characters(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["firstName"] = "a" * 25

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200
    table.put_item.assert_called_once()


def test_last_name_too_long(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["lastName"] = "a" * 26

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Last name is too long"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_last_name_exactly_25_characters(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["lastName"] = "a" * 25

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200
    table.put_item.assert_called_once()


def test_email_too_long(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["email"] = "a" * 51

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Email address is too long"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_email_exactly_50_characters(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["email"] = "a" * 45 + "@b.co"

    assert len(event_data["email"]) == 50

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200
    table.put_item.assert_called_once()


def test_reason_too_long(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["reason"] = "a" * 21

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Reason is too long"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


def test_reason_exactly_20_characters(mocked_aws):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["reason"] = "a" * 20

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200
    table.put_item.assert_called_once()


# ---------------------------------------------------------
# Email validation
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "email",
    [
        "invalid",
        "invalid@",
        "@example.com",
        "invalid@example",
        "invalid example@test.com",
    ],
)
def test_invalid_email(mocked_aws, email):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data["email"] = email

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        "Invalid email address"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


# ---------------------------------------------------------
# Input types
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("firstName", 123),
        ("lastName", 123),
        ("email", 123),
        ("reason", 123),
        ("message", 123),
        ("firstName", None),
        ("lastName", None),
        ("email", None),
        ("reason", None),
        ("message", None),
    ],
)
def test_required_fields_must_be_strings(mocked_aws, field, value):
    table, ses = mocked_aws

    event_data = json.loads(valid_event()["body"])
    event_data[field] = value

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 400
    assert get_response_body(result)["message"] == (
        f"{field} is required"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()


# ---------------------------------------------------------
# DynamoDB behaviour
# ---------------------------------------------------------


def test_dynamodb_receives_correct_enquiry(mocked_aws):
    table, ses = mocked_aws

    event_data = {
        "firstName": "  Erik  ",
        "lastName": "  Zukov  ",
        "email": "  visitor@example.com  ",
        "reason": "  Project  ",
        "message": "  Hello there.  ",
        "website": ""
    }

    result = lambda_function.lambda_handler(
        {"body": json.dumps(event_data)},
        None
    )

    assert result["statusCode"] == 200

    table.put_item.assert_called_once()

    stored_item = table.put_item.call_args.kwargs["Item"]

    assert stored_item["firstName"] == "Erik"
    assert stored_item["lastName"] == "Zukov"
    assert stored_item["email"] == "visitor@example.com"
    assert stored_item["reason"] == "Project"
    assert stored_item["message"] == "Hello there."

    assert "id" in stored_item
    assert stored_item["id"]
    assert "createdAt" in stored_item
    assert stored_item["createdAt"]


def test_dynamodb_failure_returns_500(mocked_aws):
    table, ses = mocked_aws

    table.put_item.side_effect = Exception("DynamoDB failure")

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 500
    assert get_response_body(result)["message"] == (
        "Internal server error"
    )

    ses.send_email.assert_not_called()


# ---------------------------------------------------------
# SES behaviour
# ---------------------------------------------------------


def test_ses_sends_two_emails(mocked_aws):
    table, ses = mocked_aws

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 200
    assert ses.send_email.call_count == 2


def test_notification_email_is_correct(mocked_aws):
    table, ses = mocked_aws

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 200

    notification = ses.send_email.call_args_list[0].kwargs

    assert notification["Source"] == "Erik Z <erik@erikthedev.com>"
    assert notification["Destination"]["ToAddresses"] == [
        "erik@erikthedev.com"
    ]
    assert notification["ReplyToAddresses"] == [
        "visitor@example.com"
    ]

    assert notification["Message"]["Subject"]["Data"] == (
        "AWS Outreach PP: [Project] Erik Zukov"
    )

    body = notification["Message"]["Body"]["Text"]["Data"]

    assert "Erik Zukov" in body
    assert "visitor@example.com" in body
    assert "Project" in body
    assert "I'd like to discuss a project." in body
    assert "Enquiry ID:" in body
    assert "Received:" in body


def test_confirmation_email_is_correct(mocked_aws):
    table, ses = mocked_aws

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 200

    confirmation = ses.send_email.call_args_list[1].kwargs

    assert confirmation["Source"] == "Erik Z <erik@erikthedev.com>"
    assert confirmation["Destination"]["ToAddresses"] == [
        "visitor@example.com"
    ]

    assert confirmation["Message"]["Subject"]["Data"] == (
        "Thanks for reaching out"
    )

    body = confirmation["Message"]["Body"]["Text"]["Data"]

    assert "Hi Erik," in body
    assert "Thanks for reaching out through my website." in body
    assert "within 4 days." in body
    assert "Best," in body
    assert "Erik" in body


def test_ses_failure_returns_500(mocked_aws):
    table, ses = mocked_aws

    ses.send_email.side_effect = Exception("SES failure")

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 500
    assert get_response_body(result)["message"] == (
        "Internal server error"
    )

    table.put_item.assert_called_once()


# ---------------------------------------------------------
# Unexpected errors
# ---------------------------------------------------------


def test_unexpected_error_returns_500(mocked_aws, monkeypatch):
    table, ses = mocked_aws

    monkeypatch.setattr(
        lambda_function.uuid,
        "uuid4",
        Mock(side_effect=RuntimeError("Unexpected failure"))
    )

    result = lambda_function.lambda_handler(valid_event(), None)

    assert result["statusCode"] == 500
    assert get_response_body(result)["message"] == (
        "Internal server error"
    )

    table.put_item.assert_not_called()
    ses.send_email.assert_not_called()



def test_html_maxlength_matches_lambda():
    html = Path("site/contact.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for field, expected_limit in lambda_function.VALIDATION_LIMITS.items():
        element = soup.find(attrs={"name": field})

        assert element is not None, (
            f"HTML field '{field}' was not found"
        )

        assert element.get("maxlength") == str(expected_limit), (
            f"{field}: HTML maxlength is "
            f"{element.get('maxlength')}, "
            f"but Lambda limit is {expected_limit}"
        )