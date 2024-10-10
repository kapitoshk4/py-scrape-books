import re
from typing import Any, Optional, Dict

import scrapy
from scrapy.http import Response

ratings = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/"
    ]

    def parse(self, response: Response) -> Optional[scrapy.Request]:
        for book in response.css(".product_pod"):
            book_url = book.css("h3 > a::attr(href)").get()
            if book_url:
                yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Dict[str, Any]:
        availability_text = response.css("p.instock.availability::text").getall()
        availability_text = "".join(availability_text).strip()
        rating_class = response.css("p.star-rating::attr(class)").get().split()[1]
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": float(response.css("p.price_color::text").get().replace("£", "")),
            "amount_in_stock": int(re.search(r"\((\d+)", availability_text).group(1)),
            "rating": int(ratings.get(rating_class, 0)),
            "category": response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css("table.table-striped tr:first-child td::text").get()
        }
