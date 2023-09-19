import time

from firebase_admin import db

from .models import GroupUpdateRequest


class DataHolder:
    CACHE_EXPIRE_PERIOD = 60
    def __init__(self):
        self._data: dict = None
        self._formated_data: list = None
        self._etag: str = None
        self._timestamp = 0

    def _update_data(self, force=False):
        if self._etag and not force:
            changed, data, etag = db.reference("/jx3/group/data").get_if_changed(etag=self._etag)
            if changed:
                self._data, self._etag = data, etag
        else:
            self._data, self._etag = db.reference("/jx3/group/data").get(etag=True)
        self._formated_data = self._format_data(self._data)
        self._timestamp = time.time()

    def _format_data(self, data):
        return sorted([[d["group"], d["description"], d["date"]] for d in data.values()], key=lambda x: x[2], reverse=True)

    def get_data(self, force=False):
        if self._data is None or force or time.time() - self._timestamp > self.CACHE_EXPIRE_PERIOD:
            self._update_data()
        return self._formated_data

    def add_group(self, data: GroupUpdateRequest):
        ref = db.reference(f"/jx3/group/data")
        ref.push().set({
            "group": data.group,
            "description": data.description,
            "date": data.date,
        })
        self._update_data(force=True)
        return True


data_holder = DataHolder()
