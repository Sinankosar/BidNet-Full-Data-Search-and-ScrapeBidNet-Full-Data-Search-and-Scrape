import scrapy
from scrapy_playwright.page import PageMethod


class BidspiderSpider(scrapy.Spider):
    name = "bidspider"
    def start_requests(self):
        search = "software" # write here anything you want for search .
        
        yield scrapy.Request(
            "https://www.bidnetdirect.com/",
            callback=self.parse,                      
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "input[name='keywords']"),
                    PageMethod("fill", "input[name='keywords']", search),
                    PageMethod("press", "input[name='keywords']", "Enter"),
                    PageMethod("wait_for_timeout", 5000),
                    PageMethod("wait_for_selector", ".mets-table-row"),
                ],
            },
        )

    def parse(self, response):
        rows = response.css("td.mainCol")
        self.logger.info(f"Bulunan sonuç sayısı: {len(rows)}")

        for r in rows:
            
            item = {
                "title": r.css("a span span.rowTitle::text").get("").strip(), 
                "link": "https://www.bidnetdirect.com/" + str(r.css("a::attr(href)").get("").strip()),
                "location":r.css("a span span.location::text").get("").strip(),
                "published":r.css("a span span.datesCol span.datesContent span.publicationDate span.dateValue::text").get("").strip(),
                "closing_date":r.css("a span span.datesCol span.datesContent span.closingDate.open span.dateValue::text").get("").strip(),
            }
 

            if not item["title"]:                    
                continue

            yield item
            
        next_btn = response.css("div.mets-page-navigation-control.mets-page-navigation-next a.next::attr(href)").get()
        if next_btn:
            yield response.follow(next_btn, callback=self.parse)
            # yield scrapy.Request("https://www.bidnetdirect.com" + next_btn, callback=self.parse)