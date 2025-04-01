from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pandas as pd
import numpy as np
import urllib.request
import time
import os  # Added for directory operations


class AmazonScraper:
    def __init__(self, url):
        # Set up Firefox driver
        firefox_options = Options()
        # Uncomment for headless mode
        # firefox_options.add_argument("--headless")
        
        self.driver = webdriver.Firefox(options=firefox_options)
        self.url = url
        self.product_data = {
            'Description': [],
            'Price': [],
            'Image URL': [],
            'Rate': [],
            'Total Rate': []
        }
    
    def load_page(self):
        """Load the Amazon search page"""
        print(f"Loading URL: {self.url}")
        self.driver.get(self.url)
        # Wait for page to load
        time.sleep(3)
        print("Page loaded successfully")
    
    def extract_product_data(self):
        """Extract product data from the search results page"""
        print("Extracting product data...")
        
        # Find all product sections
        products_sections = self.driver.find_elements(By.XPATH, "//div[@class='a-section a-spacing-base']")
        print(f"Found {len(products_sections)} product sections")
        
        for section in products_sections:
            try:
                # Extract description/title
                try:
                    description = section.find_element(By.XPATH, ".//span[@class='a-size-base-plus a-color-base a-text-normal']").text.strip()
                    self.product_data['Description'].append(description)
                except NoSuchElementException:
                    print("Could not find description")
                    self.product_data['Description'].append(np.NAN)
                
                # Extract price
                try:
                    price = section.find_element(By.XPATH, ".//span[@class='a-price-whole']").text.strip()
                    self.product_data['Price'].append(price)
                except NoSuchElementException:
                    print("Could not find price")
                    self.product_data['Price'].append(np.NAN)
                
                # Extract image URL
                try:
                    img_url = section.find_element(By.XPATH, ".//img[@class='s-image']").get_attribute('src')
                    self.product_data['Image URL'].append(img_url)
                except NoSuchElementException:
                    print("Could not find image URL")
                    self.product_data['Image URL'].append(np.NAN)
                
                # Extract rating
                try:
                    rate = section.find_element(By.XPATH, ".//span[contains(@class, 'a-icon-alt')]").get_attribute('innerHTML')
                    self.product_data['Rate'].append(rate)
                except NoSuchElementException:
                    print("Could not find rating")
                    self.product_data['Rate'].append(np.NAN)
                
                # Extract total ratings
                try:
                    total_rate = section.find_element(By.XPATH, ".//span[@class='a-size-base s-underline-text']").text.strip()
                    self.product_data['Total Rate'].append(total_rate)
                except NoSuchElementException:
                    print("Could not find total ratings")
                    self.product_data['Total Rate'].append(np.NAN)
                
            except Exception as e:
                print(f"Error extracting data: {e}")
        
        print(f"Extracted data for {len(self.product_data['Description'])} products")
    
    def save_to_csv(self, filename):
        """Save the extracted data to a CSV file"""
        print(f"Saving data to {filename}")
        df = pd.DataFrame(self.product_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    def download_images(self, directory="images"):
        """Download product images to a folder"""
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        
        for i, url in enumerate(self.product_data['Image URL']):
            if pd.notna(url):
                try:
                    # Create filename based on product description if available
                    if i < len(self.product_data['Description']) and pd.notna(self.product_data['Description'][i]):
                        description = self.product_data['Description'][i]
                        safe_name = "".join(c if c.isalnum() else "_" for c in description)[:30]
                        filename = f"{directory}/product_{i}_{safe_name}.jpg"
                    else:
                        filename = f"{directory}/product_{i}.jpg"
                    
                    # Download image
                    urllib.request.urlretrieve(url, filename)
                    print(f"Downloaded image {i+1}/{len(self.product_data['Image URL'])} to {filename}")
                except Exception as e:
                    print(f"Error downloading image {i+1}: {e}")
    
    def save_dom_elements(self, directory="dom_elements"):
        """Save DOM elements of product sections to separate files"""
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        
        # Find all product sections
        products_sections = self.driver.find_elements(By.XPATH, "//div[@class='a-section a-spacing-base']")
        print(f"Found {len(products_sections)} product sections")
        
        # Save each section's HTML to a separate file
        for i, section in enumerate(products_sections):
            html_content = section.get_attribute('outerHTML')
            
            # Try to get a descriptive filename if description exists
            if i < len(self.product_data['Description']) and pd.notna(self.product_data['Description'][i]):
                description = self.product_data['Description'][i]
                safe_name = "".join(c if c.isalnum() else "_" for c in description)[:30]
                filename = f"{directory}/product_{i}_{safe_name}.html"
            else:
                filename = f"{directory}/product_{i}.html"
            
            # Save HTML content to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"Saved DOM element to {filename}")
        
        # Save full page source as reference
        with open(f"{directory}/full_page.html", 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print(f"Saved full page HTML to {directory}/full_page.html")
    
    def close(self):
        """Close the browser"""
        print("Closing browser")
        self.driver.quit()


def main():
    # Add your Amazon search URL here - for example pet products search
    search_url = 'https://www.amazon.com/s?k=pet+products'
    scraper = AmazonScraper(search_url)
    
    try:
        scraper.load_page()
        scraper.extract_product_data()
        scraper.save_to_csv('Amazon Product Scraping.csv')
        
        # Save DOM elements to a separate folder
        scraper.save_dom_elements()
        
        # Uncomment the line below to download images
        # scraper.download_images()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()