import logging
from enum import Enum

import click
import asyncio

try:
    from contextlib2 import suppress
except:
    from contextlib import suppress

# from backend import app, flask_injector, Scraper
import os
import sys

project_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.getcwd()))

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_injector import FlaskInjector
from injector import singleton

from backend.api import API_HANDLERS
from backend.api.api_json_encoder import ApiJSONEncoder
from backend.config.config import config
from pony.flask import Pony

from backend.model.entities import DB
from backend.scrape import Scraper
from backend.services import SERVICES

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(config)
Pony(app)
CORS(app, resources=r'/*', allow_headers="Content-Type")
app.json_encoder = ApiJSONEncoder
api = Api(app=app)

for handler in API_HANDLERS:
    api.add_resource(handler, handler.ENDPOINT)


def configure(binder):
    db = DB(**app.config['PONY'])
    db.model.generate_mapping(create_tables=True)
    binder.bind(DB, to=db, scope=singleton)
    for service in SERVICES:
        binder.bind(service, scope=singleton)

flask_injector = FlaskInjector(app=app, modules=[configure])



def create_logger():
    import time
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    fh = logging.FileHandler(os.path.join(project_dir, "logs", f"{time.strftime('%H_%M_%b_%d_%Y')}.log"))
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class ServerType(Enum):
    All = "all",
    Backend = "backend",
    Scraper = "scraper"

    def from_name(name):
        return {"all": ServerType.All, "backend": ServerType.Backend, "scraper": ServerType.Scraper}.get(name,
                                                                                                         ServerType.All)


@click.command()
@click.option("--port", default="5000", help="port of REST api", required=False)
@click.option("--type", default="all", help="type of running: all, back, scraper", required=False)
@click.option('--output_filename', default="articles.csv", help="file for writing output of scraper", required=False)
def main(output_filename="articles.csv", port="5000", type="all"):
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.get_event_loop()
    # loop.add_signal_handler(signal.SIGINT, loop.stop)
    # asyncio.set_event_loop(loop)
    server_type = ServerType.from_name(type)
    if server_type == ServerType.Scraper:
        loop.run_until_complete(start_scraper(output_filename=output_filename))
    elif server_type == ServerType.Backend:
        loop.run_until_complete(start_back(port=port))
    elif server_type == ServerType.All:
        loop.create_task(start_scraper(output_filename=output_filename))
        # loop.create_task(start_back(debug=True, threaded=False, port=port))
    # TODO: Add signals support here
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            loop.stop()
            pending = asyncio.Task.all_tasks(loop=loop)
            for task in pending:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    loop.run_until_complete(task)
        except KeyboardInterrupt:
            pass

@asyncio.coroutine
async def start_back(*args, **kwargs):
    logger.info('start back')
    app.run(**kwargs)

@asyncio.coroutine
async def start_scraper(*args, **kwargs):
    logger.info('start scraper')
    scraper = flask_injector.injector.get(Scraper)
    await scraper.run_spiders(args, kwargs)

@asyncio.coroutine
async def start_all(*args, **kwargs):
    await asyncio.gather(start_scraper(args, kwargs), start_back(args, kwargs))


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    # logger = create_logger()
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    main()
