from backend.services.altmetric_service import AltmetricService
from backend.services.article_service import ArticleService
from backend.services.author_service import AuthorService
from backend.services.collection_service import CollectionService
from backend.services.feeds_service import FeedsService
from backend.services.geocoder_service import GeocoderService
from backend.services.institute_service import InstituteService
from backend.services.pdf_extractor import PdfExtractorService
from backend.services.rxivist_service import RxivistService
from backend.services.twitter_service import TwitterService

SERVICES = [
    AltmetricService,
    ArticleService,
    AuthorService,
    CollectionService,
    FeedsService,
    GeocoderService,
    InstituteService,
    PdfExtractorService,
    RxivistService,
    TwitterService
]
