import json
import requests
import schedule
import time
from bs4 import BeautifulSoup
from datetime import datetime
import logging

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger(__name__)

webhook_url = 'https://hooks.slack.com/services/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'
headers = {'Content-type': 'application/json'}

listing_titles = set()
collected_listings = []

def query_cl_send_to_slack():
  logger.info('Querying Craigslist...')
  url = "https://sfbay.craigslist.org/search/apa?search_distance=1.5&postal=94110&max_price=6000&min_bedrooms=3&max_bedrooms=3&min_bathrooms=2&max_bathrooms=4&availabilityMode=0&housing_type=1&housing_type=2&housing_type=3&housing_type=4&housing_type=5&housing_type=6&housing_type=7&housing_type=8&housing_type=9&housing_type=10&laundry=1&laundry=2&laundry=3&sale_date=all+dates";
  response = requests.get(url)
  parsed_html = BeautifulSoup(response.text, 'html.parser') 
  # print(parsed_html.prettify())

  posts = parsed_html.find_all('li', attrs={'class':'result-row'})

  for post in posts:
    price = post.find('span', attrs={'class':'result-price'}).string
    time_posted = post.find('time', attrs={'class':'result-date'})['datetime']

    listing = post.find('a', attrs={'class':'hdrlnk'})
    title = listing.string
    link = listing['href']

    logging.info('POST "%s" - %s - %s - %s - %s', title, link, listing, price, time_posted)

    if title not in listing_titles:
      listing_titles.add(title)
      timestamp = datetime.strptime(time_posted, '%Y-%m-%d %H:%M')

      collected_listings.append({
        'time': timestamp,
        'title': title,
        'link': link,
        'price': price,
      })

  collected_listings.sort(key=lambda x: x['time'], reverse=True)

  payload = {
    'text': 'Your digest of Craigslist apartments, sorted by most recently posted',
    'attachments': [
    ]
  }
  for listing in collected_listings:
    message = {
      'title': listing['title'],
      'title_link': listing['link'],
      'fields': [
        {
          "value": listing['price'],
          "short": "false"
        },
        {
          "value": listing['time'].strftime('%m/%d/%Y %H:%M'),
          "short": "false"
        }
      ]
    }
    payload['attachments'].append(message)

  logging.info('Posting to Slack!')
  r = requests.post(webhook_url, data=json.dumps(payload), headers=headers)


# query_cl_send_to_slack()

# schedule.every(1).minutes.do(query_cl_send_to_slack)
schedule.every().day.at("18:48").do(query_cl_send_to_slack)
schedule.every().day.at("18:52").do(query_cl_send_to_slack)
# schedule.every().day.at("22:00").do(query_cl_send_to_slack)

while True: 
  # Checks whether a scheduled task  
  # is pending to run or not 
  schedule.run_pending() 
  time.sleep(1)

