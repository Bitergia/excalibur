class CornerStoneMetadata:
    def __init__(self):
        self.uuid = None
        self.parent_uuid = None
        self.raw_uuid = None
        self.perceval_updated_on_ts = None
        self.model_version = None
        self.type = None
        self.subtype = None
        self.origin = None
        self.tag = None
        self.backend_version = None
        self.retrieval_ts = None
        self.processed_ts = None
        self.arthur_job_id = None
        # TODO: check self.fingerprint = None

class CornerStoneItem:
    def __init__(self):
        self.metadata = None
        self.data = None
        self.data_ext = None
