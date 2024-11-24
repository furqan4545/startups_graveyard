from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import requests
from bs4 import BeautifulSoup
import time
import openai 
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")

# Define Edge options
options = Options()
# options.add_argument('--headless')
openai.api_key = OPENAI_API_KEY


service = Service(executable_path='/Users/top_g/Desktop/python/Team-eden-data-scrapper/msedgedriver.exe')

def scrape_website(url):

    while url:
        # Download the webpage with Requests
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        
        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')
        html_content = soup.prettify()
        print(html_content)
        with open('output.txt', 'w') as f:
            # Write the HTML content to the file
            f.write(html_content)
        tt = int(len(html_content) / 2)
        print("leennnn",tt)
        # Split the HTML content into smaller chunks
        # chunks = [html_content[i:i+tt] for i in range(0, len(html_content), tt)]
        # for chunk in chunks:
        #     # print(chunk)
        #     print("=====================================")
        #     response = openai.ChatCompletion.create(
        #         model="gpt-4-0613",
        #         messages=[
        #             {"role": "system", "content": "You are a helpful assistant."},
        #             {"role": "user", "content": f"Given the following HTML, find the html element that help selenium to navigate to next page. or look for pagination element. Here is html : \n\n{chunk}"},
        #         ]
        #         # max_tokens=12000,
        #     )
        #     selector = response['choices'][0]['message']['content'].strip()
        #     print(selector)
        # print(chunks)


        # divide soup text chunk into 2 parts 
        


            
        # gg = soup[:tt]
        # print(len(soup.prettify()))
        
        # Process the HTML in any way you need...
        # For example, you might want to find and print all <p> elements:
        # for p in soup.find_all('p'):
        #     print(p.get_text())
        break

        # response = openai.ChatCompletion.create(
        #     model="gpt-4-0613",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": f"Given the following HTML, predict the CSS selector or XPath of the 'Next' button:\n\n{soup.prettify()}"},
        #     ]
        #     # max_tokens=12000,
        # )

        # # Get the predicted CSS selector or XPath from the model's response
        # selector = response['choices'][0]['message']['content'].strip()
        # print(f"Predicted selector: {selector}")

    
    # driver = webdriver.Edge(service=service, options=options)
    # driver.get(url)

    # html = driver.page_source
    # soup = BeautifulSoup(html, 'html.parser')

    # pages = soup.find_all('a', href=True)

    # for page in pages:
    #     url = page['href']
    #     contents = requests.get(url).content

    #     with open(url, 'wb') as f:
    #         f.write(contents)

    # driver.quit()


if __name__ == '__main__':
    url = "https://www.law.go.kr/LSW/eng/engLsSc.do?menuId=2&query="

    scrape_website(url)

