import json
from http import HTTPStatus

from marshmallow import ValidationError

from service_api.applications.logger.logger import app_logger
from service_api.applications.response import Response
from service_api.domain.announcements import Announcements
from service_api.forms import AnnouncementDeserializer, AnnouncementSerializer


def get_announcements(event, context):
    query_params = event["queryStringParameters"] or {}
    limit, offset = int(query_params.get("limit", 10)), query_params.get("offset")

    try:
        announcements, next_offset = Announcements.get_announcements(limit, offset)
    except Exception:
        app_logger.exception("An unexpected error has occurred")
        return Response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {"message": "An unexpected error has occurred"}
        ).json

    try:
        serialized_announcements = AnnouncementSerializer(many=True).dumps(announcements)
    except ValidationError as e:
        app_logger.exception("ValidationError")
        return Response(HTTPStatus.BAD_REQUEST, {"message": e.messages}).json

    return Response(
        status_code=HTTPStatus.OK,
        body=serialized_announcements,
        headers={"next_offset": next_offset}
    ).json


def create_announcements(event, context):

    try:
        payload = json.loads(event["body"])
        payload = AnnouncementDeserializer(many=isinstance(payload, list)).load(payload)
    except json.JSONDecodeError:
        app_logger.exception("JSONDecodeError")
        return Response(HTTPStatus.BAD_REQUEST, {"message": "Wrong json format"}).json
    except ValidationError as e:
        app_logger.exception("ValidationError")
        return Response(HTTPStatus.BAD_REQUEST, {"message": e.messages}).json

    try:
        announcement = Announcements.create_announcements(payload)
    except Exception:
        app_logger.exception("An unexpected error has occurred")
        return Response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {"message": "An unexpected error has occurred"}
        ).json

    try:
        serialized_announcement = AnnouncementSerializer(many=isinstance(payload, list)).dumps(announcement)
    except ValidationError as e:
        app_logger.exception("ValidationError")
        return Response(HTTPStatus.BAD_REQUEST, {"message": e.messages}).json

    return Response(HTTPStatus.CREATED, serialized_announcement).json


def get_announcement(event, context):
    announcement_id = event['pathParameters']['id']

    try:
        announcement_id = int(announcement_id)
    except ValueError:
        app_logger.exception("Can't convert '%s' to int" % announcement_id)
        return Response(
            HTTPStatus.BAD_REQUEST,
            {"message": f"Value '{announcement_id}' should be a number"}
        ).json

    try:
        announcement = Announcements.get_announcement(announcement_id)
    except Exception:
        app_logger.exception("An unexpected error has occurred")
        return Response(
            HTTPStatus.INTERNAL_SERVER_ERROR,
            {"message": "An unexpected error has occurred"}
        )

    try:
        serialized_announcement = AnnouncementSerializer().dumps(announcement)
    except ValidationError as e:
        app_logger.exception("ValidationError")
        return Response(HTTPStatus.BAD_REQUEST, {"message": e.messages}).json

    return Response(HTTPStatus.OK, serialized_announcement).json
