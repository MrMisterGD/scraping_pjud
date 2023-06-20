from app.init import app
from scrapy.crawler import CrawlerRunner
from app.models.recaspider.recaspider.spiders.recaspider_ver1 import Recaspider
from flask import Response
from scrapy.utils.project import get_project_settings
import app.models.pjudspider.pjudspider_bs4
import threading

results = []
event = threading.Event()

def scrape_data(rut, dv, rit):
    runner = CrawlerRunner(get_project_settings())
    print("scrape data:", rut + "-" + dv, "RIT:", rit)
    spider_cls = Recaspider
    deferred = runner.crawl(spider_cls, rut=rut, dv=dv, rit=rit)
    deferred.addBoth(lambda _: event.set())
    deferred.addCallback(collect_results, rut, dv, rit)
    return deferred

def collect_results(_, rut, dv):
    global results
    results = Recaspider.results

@app.route('/<rut>-<dv>/<ritlibro>-<ritnumero>-<ritanio>', methods=['GET'])
def initiate_scraping(rut, dv, ritlibro, ritnumero, ritanio):
    print("scraping data:", rut + "-" + dv, "RIT:", ritlibro + "-" + ritnumero + "-" + ritanio)
    deferred = scrape_data(rut, dv)
    event.wait()
    return Response(response='Scraping completed. Results:\n\n{}'.format(results), status=200, mimetype='text/plain')