import re
import os
from pymongo import MongoClient
from rembg import remove
# from icrawler.builtin import GoogleImageCrawler
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler
from PIL import Image
from duckduckgo_search import DDGS
import requests
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

# MongoDB connection setup
# MONGO_URI = os.environ.get('MONGODB_CONNECTION_STRING')
MONGO_URI =  "mongodb+srv://transpify-db:N0zffLB2DUbox9o7@cluster0.y52sco2.mongodb.net/Transpify?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["Transpify"]  # Adjust the database name as necessary
person_data_collection = db["aistudio_scrapper_person"] # Adjust the collection name as necessary
company_data_collection = db["aistudio_scrapper_company"] 
# Environment variables for Azure Blob Storage
# storage_account_key = os.environ.get('STORAGE_ACCOUNT_KEY')
# storage_account_name = os.environ.get('STORAGE_ACCOUNT_NAME')
# storage_container_name_video = "aistudio"
# storage_connection_string = os.environ.get('STORAGE_CONNECTION_STRING')

storage_account_key = "9vvvwn7iKr8ANGwK+6yQNB+uCNdHROghOTA/bU9fXrwww2odGNAtYKtyJn6MSlLpe0xIqxmyjIcj+AStHokFHA=="
storage_account_name = "transpifyblob"
storage_connection_string = "DefaultEndpointsProtocol=https;AccountName=transpifyblob;AccountKey=9vvvwn7iKr8ANGwK+6yQNB+uCNdHROghOTA/bU9fXrwww2odGNAtYKtyJn6MSlLpe0xIqxmyjIcj+AStHokFHA==;EndpointSuffix=core.windows.net"
# storage_container_name_video = "aistudio"
storage_container_name_video = "transpifyvideos"

def upload_to_azureBlob_and_get_url(subcontainer, file_path):
    """
    Uploads a file to Azure Blob Storage and returns a SAS URI with 3 months expiry.
    """
    # absolute_path = os.path.abspath(file_path)
    
    # # Check if the file exists before trying to upload
    # if not os.path.exists(absolute_path):
    #     print(f"File not found: {absolute_path}")
    #     return None  # Or handle this error as needed
    
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    azure_path = f"{subcontainer}/{os.path.basename(file_path)}"
    blob_client = blob_service_client.get_blob_client(container=storage_container_name_video, blob=azure_path)

    # Upload the file
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    # Generate SAS token for the blob
    sas_token = generate_blob_sas(account_name=storage_account_name,
                                  container_name=storage_container_name_video,
                                  blob_name=azure_path,
                                  account_key=storage_account_key,
                                  permission=BlobSasPermissions(read=True),
                                  expiry=datetime.utcnow() + timedelta(weeks=9000))  # 3 months expiry

    # Construct the SAS URL for the blob
    sas_url = f"https://{storage_account_name}.blob.core.windows.net/{storage_container_name_video}/{azure_path}?{sas_token}"
    return sas_url



def company_url_search(query):
    """
    Returns the official website URL for a given company name using DuckDuckGo search.
    """
    
    # Initialize the DuckDuckGo search object and get the first result
    url = ""
    with DDGS() as ddgs:
        results = [r['href'] for r in ddgs.text(query+" official website", max_results=3)]
        url = results[0]
    
    # Return the URL
    return url

def download_and_process_image(query, type, output_folder='./icrawler_images'):
    """
    Downloads an image based on a query and removes its background.

    Parameters:
    - query: The search term for the image.
    - company: A boolean flag indicating whether the search is for a company logo. Defaults to False.
    - output_folder: The directory where the image will be saved. Defaults to 'icrawler_images'.

    The function modifies the query based on whether it's searching for a company logo or a person's image,
    downloads the first image from Google Images, removes its background, and saves the processed image
    in the specified output folder with a clean, descriptive filename.
    """
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)
    if type == "company":
        modified_query = f"{query} logo png"
    elif type == "person":
        # modified_query = f"{query} png"
        modified_query = f"{query} png"
    else:
        modified_query = query
    
    # Initialize the GoogleImageCrawler with the specified output folder
    google_crawler = GoogleImageCrawler(storage={'root_dir': output_folder})
    # google_crawler = BingImageCrawler(storage={'root_dir': output_folder})
    
    # Start the crawl process
    # google_crawler.crawl(keyword=modified_query, max_num=1, overwrite=True)
    google_crawler.crawl(keyword=modified_query, max_num=1, overwrite=True)
    
    # Get the name of the downloaded file (assumes only one file is downloaded)
    downloaded_files = os.listdir(output_folder)
    if not downloaded_files:
        print("No images downloaded.")
        return
    
    downloaded_file = downloaded_files[0]

    # Define the new filename, removing unnecessary parts for clarity
    new_filename = f"{query.replace(' ', '')}.png"

    # Process the image: open, remove background, and save
    try:
        with Image.open(os.path.join(output_folder, downloaded_file)) as image_downloaded:
            output_with_no_bg = remove(image_downloaded)
            output_with_no_bg.save(os.path.join(output_folder, new_filename), format='PNG')
            print(f"Processed and saved image as {new_filename} successfully.")
    except Exception as e:
        print(f"An error occurred during image processing: {e}")
        return

    # Cleanup: remove the original downloaded file
    if os.path.exists(os.path.join(output_folder, downloaded_file)):
        os.remove(os.path.join(output_folder, downloaded_file))

    #Return a new path (NOTE: It will be deleted after uploading it to azure Blob Storage)
    return os.path.join(output_folder, new_filename)




def scrapper_pipeline(query, query_type, user_id, video_id):
    """
    Orchestrates the image download and processing pipeline for either a person or a company.

    Args:
    - query: The search query (person name or company name).
    - query_type: Type of query ('person' or 'company').

    Returns:
    - A dictionary containing the data that already inserted into the database.
    """

    # Download and process the image
    image_path = download_and_process_image(query, query_type)
    new_data = {}
    

    if query_type == "person":
        image_url = upload_to_azureBlob_and_get_url(f"{user_id}/{video_id}/person/images", image_path)
        new_data = {
            "person_name": query,
            "image_url": image_url
        }
        person_data_collection.insert_one(new_data)


    elif query_type == "company":
        logo_url = upload_to_azureBlob_and_get_url(f"{user_id}/{video_id}/company_data/logos", image_path)
        url = company_url_search(query)
        print(f"The URL for {query} is: {url}")

        # Run a node command to create a website video

        width = 1600 #Tune it later as needed
        height = 900 #Tune it later as needed
        
        os.system(f"node create_website_video.js {url} {width} {height}")
        
        #It will save the video as url.mp4 without https:// or http:// in root project directory

        website_video_path = re.sub(r'[/:\\%*?<>|"\\]', '_', re.sub(r'/$', '', re.sub(r'^https?://', '', url))) + '.mp4'
        
        # Now we will upload data to azure blob storage and get the sas url
        website_video_url = upload_to_azureBlob_and_get_url(f"{user_id}/{video_id}/company_data/website_videos", website_video_path)

        # Now we will test if the company has /pricing page or not url+"/pricing" if it exists then the response will be 200 using requests library
        pricing_url = f"{url}/pricing"
        response = requests.get(pricing_url)
        if response.status_code == 200:
            print("The company has a pricing page")
            
            # Run a node command to create a pricing video
            os.system(f"node create_website_video.js {pricing_url} {width} {height}")
            website_pricing_video_path = re.sub(r'[/:\\%*?<>|"\\]', '_', re.sub(r'/$', '', re.sub(r'^https?://', '', pricing_url))) + '.mp4'            
            website_pricing_video_url = upload_to_azureBlob_and_get_url(f"{user_id}/{video_id}/company_data/website_pricing_videos", website_pricing_video_path)
        else:
            print("The company does not have a pricing page")
            # If the company does not have a pricing page, set the pricing video URL to None
            website_pricing_video_url = None

        # Insert the data into the database
        new_data = {
            "user_id": user_id,
            "video_id": video_id,
            "company_name": query,
            "logo_url": logo_url,
            "website_url": url,
            "website_video_url": website_video_url,
            "website_pricing_video_url": website_pricing_video_url
        }
        company_data_collection.insert_one(new_data)
        
    return new_data


# # Example usage
# if __name__ == "__main__":
#     # query = "Figma"
#     # type = "company"
#     # result = scrapper_pipeline(query, type)
#     # print(result)
#     query = "andrew"
#     type = "person"
#     result = scrapper_pipeline(query, type, "furqan", "06206327ce")
    
#     # # # delete all the images from local folder
#     if os.path.exists("./icrawler_images"):
#         for file in os.listdir("icrawler_images"):
#             os.remove(os.path.join("icrawler_images", file))
#     print(result)
    
    
    