from app.services.extendedObjectStorage_service import ExtendedObjectStorage

def create_object(obj_name, obj_path, file):
    res = ExtendedObjectStorage.create_object(obj_name, obj_path, file)
    if (res.success):
        return res, 201

    return res, 500