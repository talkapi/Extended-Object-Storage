from app.services.object_service import get_object_service
from app.services.extendedObjectStorage_service import ExtendedObjectStorage
import os.path
from flask import request

extendedStorage = ExtendedObjectStorage()


def get_object():
    args = request.args
    object_path = args.get("objectPath")
    obj_name = os.path.basename(object_path)
    obj_path = os.path.dirname(object_path)
    res = extendedStorage.get_object(obj_name, obj_path)
    return res, res['status']

def create_object():
    args = request.args
    object_path = args.get("objectPath")
    obj_name = os.path.basename(object_path)
    obj_path = os.path.dirname(object_path)
    file = request.files['file']
    res = extendedStorage.create_object(obj_name, obj_path, file)
    return res, res['status']

def delete_object():
    args = request.args
    object_path = args.get("objectPath")
    obj_name = os.path.basename(object_path)
    obj_path = os.path.dirname(object_path)
    res = extendedStorage.delete_object(obj_name, obj_path)
    return res, res['status']

def rename_object():
    object_path = request.get_json()['objectPath']
    new_name = request.get_json()['newObjectName']
    obj_name = os.path.basename(object_path)
    obj_path = os.path.dirname(object_path)
    res = extendedStorage.rename_object(obj_name, obj_path, new_name)
    return res, res['status']

def create_directory():
    res = extendedStorage.create_directory(request.get_json()['path'])
    return res, res['status']


def list_directory():
    args = request.args
    prefix_path = args.get("prefixPath")
    res = extendedStorage.list_directory(prefix_path)
    return res, res['status']

def rename_directory():
    prefixPath = request.get_json()['prefixPath']
    new_dir_path = request.get_json()['newDirPath']
    res = extendedStorage.rename_directory(prefixPath, new_dir_path)
    return res, res['status']

def delete_directory():
    args = request.args
    prefixPath = args.get("prefixPath")
    res = extendedStorage.delete_directory(prefixPath)
    return res, res['status']