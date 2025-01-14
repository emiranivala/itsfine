import threading

class BatchTemp:
    _lock = threading.Lock()
    IS_BATCH = {}

    @classmethod
    def set_batch(cls, user_id, value):
        with cls._lock:
            cls.IS_BATCH[user_id] = value

    @classmethod
    def get_batch(cls, user_id):
        with cls._lock:
            return cls.IS_BATCH.get(user_id, True)

    @classmethod
    def cancel_batch(cls, user_id):
        with cls._lock:
            cls.IS_BATCH[user_id] = True
