from backend.spiders.arxiv_spider import ArxivSpider
from backend.spiders.biorxiv_spider import BiorxivSpider
from backend.spiders.medrxiv_spider import MedrxivSpider

SPIDERS = [
    ArxivSpider,
    BiorxivSpider,
    MedrxivSpider
]