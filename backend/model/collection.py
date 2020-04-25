import dataclasses
import logging
from datetime import datetime
from enum import Enum
from typing import List
from backend.utils.misc import exception
import pickle
import pandas as pd

logger = logging.getLogger(__name__)

class CollectionDTO(dict):
    url: str
    title: str
    source: str

    def __init__(self, *args, **kwargs):
        if not kwargs:
            return
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"{self.title}"

    @exception(logger, reraise=False)
    def __getattr__(self, name):
        return self[name]

    @exception(logger, reraise=False)
    def __setattr__(self, name, value):
        self[name] = value

    @exception(logger, reraise=False)
    def __delattr__(self, name):
        del self[name]

    @staticmethod
    @exception(logger, reraise=False)
    def to_csv(articles: List[dict], filename: str):
        pd.DataFrame(articles).to_csv(filename)

    @staticmethod
    @exception(logger, reraise=False)
    def to_pickle(articles: List[dict], filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(articles, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    @exception(logger, reraise=False)
    def from_pickle(filename: str) -> List[dict]:
        with open(filename, 'rb') as f:
            return pickle.load(f)
