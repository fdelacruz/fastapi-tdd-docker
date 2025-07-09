from pydantic import Basemodel


class SummaryPayloadSchema(Basemodel):
    url: str
