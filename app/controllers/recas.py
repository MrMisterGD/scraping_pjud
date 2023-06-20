from app.init import app
import threading
from scrapy.crawler import CrawlerRunner
from app.models.recaspider.recaspider.spiders.recaspider_ver1 import Recaspider
from flask import Response
from scrapy.utils.project import get_project_settings

results = []
event = threading.Event()

def scrape_data(rut, dv):
    runner = CrawlerRunner(get_project_settings())
    print("scrape data:", rut + "-" + dv)
    spider_cls = Recaspider
    deferred = runner.crawl(spider_cls, rut=rut, dv=dv)
    deferred.addBoth(lambda _: event.set())
    deferred.addCallback(collect_results, rut, dv)
    return deferred

def collect_results(_, rut, dv):
    global results
    results = Recaspider.results

@app.route('/<rut>-<dv>', methods=['GET'])
def initiate_scraping(rut, dv):
    print("scraping data:", rut + "-" + dv)
    deferred = scrape_data(rut, dv)
    event.wait()
    return Response(response='Scraping completed. Results:\n\n{}'.format(results), status=200, mimetype='text/plain')