
import html2text
import json
import requests
import re
import sys
from htmldom import htmldom

class ShopifyScraper:
    def __init__(self, root_domain):
        self.domain_url = root_domain
        self.product_list_url = self.domain_url + "/products.json"
        self.product_list = []
        self.get_shopify_url()

    # Grab the Shopify URL by scanning the webpage
    def get_shopify_url(self):     
        html = requests.get(self.domain_url)
        matches = re.search("([A-z0-9\-]+\.myshopify\.com)", html.text) 

        if (matches == None):
            print("Unable to find the myshopify url from the provided domain")
            sys.exit()

        self.shopify_url = matches.group()

    def get_product_reviews(self, product_id):
        try:
            url = f'https://productreviews.shopifycdn.com/proxy/v4/reviews/product?product_id={product_id}&version=v4&shop={self.shopify_url}'
            product = requests.get(url).json()
        except:
            # If reviews are not available for the site
            return [], 0

        # Check If there are any reviews for the product
        if (product["reviews"] == "" or product["aggregate_rating"] == ""):
            return [], 0

        reviews = []

        dom = htmldom.HtmlDom()
        dom = dom.createDom(product["reviews"])

        review_html = dom.find(".spr-review")
        for element in review_html:
            reviews.append(element.find('.spr-review-content-body').text())

        # Grab the aggregate_rating and convert to a dictionary
        m = re.search('<script[\s\S]*?>([\s\S]*?)<\/script>', product["aggregate_rating"])
        aggregate_rating = json.loads(m.group(1))

        return reviews, aggregate_rating["ratingValue"]

    def get_products(self):
        self.fetch_products = requests.get(self.product_list_url)
        products = self.fetch_products.json()["products"]

        for i in products:
            # Grab the reviews for the product
            reviews, rating = self.get_product_reviews(i["id"])

            self.product_list.append({
                "title": i["title"],
                "rating": rating,
                "reviews": reviews
            })


    def print_products(self):
        for product in self.product_list:
            print(product)

# Example
app = ShopifyScraper("https://shopnicekicks.com")
app.get_products()
app.print_products()
