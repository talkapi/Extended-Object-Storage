from app.services.object_service import get_object_service
from app.services.extendedObjectStorage_service import ExtendedObjectStorage
import os.path
from flask import request

extendedStorage = ExtendedObjectStorage()


def get_object():
    res = get_object_service()
    # res = get_examples_service()
    return res, 200


def create_object():
    args = request.args
    object_path = args.get("objectPath")
    obj_name = os.path.basename(object_path)
    obj_path = os.path.dirname(object_path)
    res = extendedStorage.create_object(obj_name, obj_path, request.get_data())
    return res, res['status']


def create_directory():
    res = extendedStorage.create_directory(request.get_json()['path'])
    return res, res['status']


def list_directory():
    args = request.args
    prefix_path = args.get("prefixPath")
    res = extendedStorage.list_directory(prefix_path)
    return res, res['status']

