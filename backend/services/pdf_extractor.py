import logging

from injector import inject
from tika import parser

from backend.utils.misc import exception

logger = logging.getLogger(__name__)

class PdfExtractorService:
    @inject
    def __init__(self):
        pass

    @exception(logger, reraise=False)
    def from_buffer(self, buffer) -> str:
        raw = parser.from_buffer(buffer)
        return raw['content']

    @exception(logger, reraise=False)
    def from_file(self, filename: str) -> str:
        raw = parser.from_file(filename)
        return raw['content']
