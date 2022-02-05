from app.services.object_service import get_object_service
import asyncio


def get_object():
    res = get_object_service()
    # res = get_examples_service()
    return res, 200


def insert_object():
    return {}, 200
