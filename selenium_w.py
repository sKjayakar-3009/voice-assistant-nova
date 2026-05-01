import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)
class infow:
    def __init__(self):

        try:
            chrome_options = Options()
            chrome_options.binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"
            chrome_driver_path = "C:/Users/ADMIN/Downloads/chromedriver-win64 (1)/chromedriver-win64/chromedriver.exe"
            service = Service(chrome_options=chrome_driver_path)
            self.driver = webdriver.Chrome(service=service)
            logging.info("ChromeDriver started successfully.")
        except Exception as e:
            logging.error(f"Error initializing ChromeDriver: {e}")

    def search_wikipedia(self, query):
        try:
            self.driver.get(url="https://www.wikipedia.org/")
            search = self.driver.find_element(By.XPATH, '//*[@id="searchInput"]')
            search.click()
            search.send_keys(query)
            enter = self.driver.find_element(By.XPATH, '//*[@id="search-form"]/fieldset/button')
            enter.click()

            # Extract the first paragraph using XPath
            first_paragraph = self.driver.find_element(By.XPATH, '//*[@id="mw-content-text"]/div[1]/p[2]').text
            return first_paragraph
        except Exception as e:
            logging.error(f"Error retrieving information: {e}")
            return None

    def fetch_weather(city):
        API_KEY = "7351f70bb4430b23339750725a90bf26"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                return f"Could not retrieve weather for {city}. Please try another location."

            weather_desc = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]

            return f"Weather in {city}: {weather_desc.capitalize()}, Temperature: {temperature}°C, Feels like: {feels_like}°C"
        except Exception as e:
            return "An error occurred while fetching the weather data."


    def play_youtube_video(self, topic):
        try:
            # Open YouTube and search for the video
            self.driver.get("https://www.youtube.com")
            time.sleep(2)  # Allow page to load
            search_box = self.driver.find_element(By.NAME, "search_query")
            search_box.send_keys(topic)
            search_box.send_keys(Keys.RETURN)

            # Wait for the search results and click on the first video
            time.sleep(3)
            first_video = self.driver.find_element(By.XPATH, '(//a[@id="video-title"])[1]')
            first_video.click()
            time.sleep(5)  # Wait to ensure video starts playing
        except Exception as e:
            # Log error and reset WebDriver if the session has closed
            if "no such window" in str(e) or "target window already closed" in str(e):
                print("Chrome window was closed unexpectedly. Restarting ChromeDriver...")
                self.driver.quit()
                self.start_chromedriver()  # Function to restart ChromeDriver
                # Retry playing YouTube video
                self.play_youtube_video(topic)
            else:
                print(f"Error playing YouTube video: {e}")
                self.driver.quit()


    # Example function to get and read the top news headline
    def get_news_headlines(self):
        try:
            self.driver.get("https://indianexpress.com/")  # Example news site

            # Adjusted XPath for the first headline
            first_headline_element = self.driver.find_element(By.XPATH,
                                                         '//*[@id="HP_NEWS_BREAKING"]/div/div[1]/div[2]/h1/a')

            first_headline = first_headline_element.text

            # Ellie reads the first headline
            if first_headline:
                return first_headline
            else:
                error_msg = "No headline found."
                return None

        except Exception as e:
            logging.error(f"Error fetching news headlines: {e}")
            return None

    def play_online_game(self):
        try:
            self.driver.get("https://poki.com/")  # Example game site

            # Further code to interact with the game site can be added here
        except Exception as e:
            logging.error(f"Error accessing online games: {e}")

    @staticmethod
    def search_google(query):
        # Replace with your actual API key and search engine ID
        API_KEY = "AIzaSyBB_9I9eWYgKrSUyafgMW4O0EZT2z7pXLg"
        SEARCH_ENGINE_ID = "51047a76011064371"
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"

        try:
            response = requests.get(url)
            results = response.json()

            # Extract relevant information
            output = ""
            for item in results.get("items", []):
                title = item.get("title")
                snippet = item.get("snippet")
                link = item.get("link")
                output += f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n"

            if not output:
                output = "No results found."
            return output

        except Exception as e:
            return f"An error occurred while fetching search results: {e}"
