from firebase_admin import db
import time

from .models import IQCommentUpdateRequest, IQRequest, IQUpdateRequest, IQCommentDeleteRequest, IQDeleteRequest


class DataHolder:
    CACHE_EXPIRE_PERIOD = 60
    def __init__(self):
        self._data: dict = None
        self._etag: str = None
        self._timestamp = 0

    def _update_data(self, force=False):
        if self._etag and not force:
            changed, data, etag = db.reference("/celebrity_iq/data").get_if_changed(etag=self._etag)
            if changed:
                self._data, self._etag = data, etag
        else:
            self._data, self._etag = db.reference("/celebrity_iq/data").get(etag=True)
        self._timestamp = time.time()

    def _format_data(self):
        if not self._data:
            return []
        return sorted(self._data.values(), key=lambda d: IQRequest.iq_to_number(d["iq"]), reverse=True)

    def get_data(self, force=False):
        if self._data is None or force or time.time() - self._timestamp > self.CACHE_EXPIRE_PERIOD:
            self._update_data()
        return self._format_data()

    def update_data(self, data: IQUpdateRequest):
        ref = db.reference(f"/celebrity_iq/data/{data.celebrity_name}")
        ref.update({
            "name": data.celebrity_name,
            "iq": data.iq
        })
        self._update_data(force=True)
        return True

    def delete_data(self, data: IQDeleteRequest):
        if data.celebrity_name not in self._data:
            return False
        ref = db.reference(f"/celebrity_iq/data/{data.celebrity_name}")
        ref.delete()
        self._update_data(force=True)
        return True

    def add_comment(self, data: IQCommentUpdateRequest):
        if data.celebrity_name not in self._data:
            return False
        ref = db.reference(f"/celebrity_iq/data/{data.celebrity_name}/comments")
        ref.push().set({
            "type": data.comment_type,
            "comment": data.comment,
            "score": data.comment_score
        })
        self._update_data(force=True)
        return True

    def delete_comment(self, data: IQCommentDeleteRequest):
        if data.celebrity_name not in self._data:
            return False
        ref = db.reference(f"/celebrity_iq/data/{data.celebrity_name}/comments/{data.comment_id}")
        ref.delete()
        self._update_data(force=True)
        return True

data_holder = DataHolder()
