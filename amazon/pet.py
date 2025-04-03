import datetime
import os
import random
import re
import time
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
#update
class AmazonScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.com/s?k=gaming&crid=2Q95QAJCPV7RS&sprefix=%2Caps%2C611&ref=nb_sb_ss_recent_2_0_recent"
        self.driver = None
        self.output_dir = self._create_output_dirs()

    def _create_output_dirs(self):
        """Create output directories for CSV and HTML files"""
        output_dir = os.path.join(os.getcwd(), "amazon_output")
        csv_dir = os.path.join(output_dir, "csv")
        html_dir = os.path.join(output_dir, "html")
        screenshot_dir = os.path.join(output_dir, "screenshots")
        images_dir = os.path.join(output_dir, "images")

        for directory in [output_dir, csv_dir, html_dir, screenshot_dir, images_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        return output_dir

    def _initialize_driver(self):
        """Initialize Firefox driver with custom options"""
        try:
            options = Options()

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            ]
            options.set_preference(
                "general.useragent.override", random.choice(user_agents)
            )
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", False)
            options.set_preference("browser.cache.offline.enable", False)
            options.set_preference("network.http.use-cache", False)
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f"--width={width}")
            options.add_argument(f"--height={height}")
            options.set_preference("intl.accept_languages", "en-US, en")
            # un_c for hedless
            # options.add_argument("--headless")
            return webdriver.Firefox(options=options)

        except Exception as e:
            print(f"Error initializing Firefox driver: {e}")
            return None

    def human_like_delay(self):
        """Wait for a random amount of time to simulate human behavior"""
        delay = random.uniform(1.5, 3.5)
        time.sleep(delay)

    def human_like_scroll(self, distance=None):
        """Scroll in a human-like way with random distance"""
        if not self.driver:
            print("Driver is not initialized.")
            return

        try:
            if distance is None:
                distance = random.randint(300, 800)

            self.driver.execute_script(
                f"window.scrollBy({{top: {distance}, left: 0, behavior: 'smooth'}});"
            )

            time.sleep(random.uniform(0.5, 1.5))

            if random.random() < 0.2:  # 20% chance to scroll back
                self.driver.execute_script(
                    f"window.scrollBy({{top: -{random.randint(50, 150)}, left: 0, behavior: 'smooth'}});"
                )
                time.sleep(random.uniform(0.3, 0.7))

        except Exception as e:
            print(f"Error during scrolling: {e}")

    def save_screenshot(self, name):
        """Save screenshot for debugging"""
        if not self.driver:
            print("Driver is not initialized. Cannot take screenshot.")
            return None

        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(
                self.output_dir, "screenshots", f"{name}_{timestamp}.png"
            )
            self.driver.save_screenshot(file_path)
            return file_path
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None

    def save_html(self, page_num, html_content):
        """Save the raw HTML content"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(
            self.output_dir, "html", f"amazon_page_{page_num}_{timestamp}.html"
        )

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return file_path
        except Exception as e:
            print(f"Error saving HTML: {e}")
            return None

    def extract_product_data(self, page_source):
        """Extract product data from BeautifulSoup object"""
        soup = BeautifulSoup(page_source, "html.parser")
        products = []

        product_containers = soup.select(
            'div.s-result-item[data-component-type="s-search-result"]'
        )

        if not product_containers:
            product_containers = soup.select("div.sg-col-4-of-12.s-result-item")

        if not product_containers:
            product_containers = soup.select("div.a-section.a-spacing-base")

        print(f"Found {len(product_containers)} product containers")

        for container in product_containers:
            try:
                if container.get(
                    "data-component-type"
                ) != "s-search-result" and "AdHolder" in container.get("class", []):
                    continue

                product = {}

                title_element = (
                    container.select_one("h2 a span")
                    or container.select_one(
                        ".a-size-base-plus.a-color-base.a-text-normal"
                    )
                    or container.select_one(".a-size-medium.a-color-base.a-text-normal")
                )
                product["title"] = (
                    title_element.text.strip() if title_element else "N/A"
                )

                link_element = container.select_one("h2 a") or container.select_one(
                    ".a-link-normal"
                )
                product["link"] = (
                    link_element["href"]
                    if link_element and "href" in link_element.attrs
                    else "N/A"
                )

                if product["link"] != "N/A" and not product["link"].startswith("http"):
                    product["link"] = self.base_url + product["link"]

                price_whole_element = container.select_one("span.a-price-whole")
                price_fraction_element = container.select_one("span.a-price-fraction")

                product["price_whole"] = (
                    price_whole_element.text.strip() if price_whole_element else ""
                )
                product["price_fraction"] = (
                    price_fraction_element.text.strip()
                    if price_fraction_element
                    else ""
                )
                product["price"] = (
                    f"${product['price_whole']}.{product['price_fraction']}"
                    if product["price_whole"]
                    else "N/A"
                )

                rating_element = container.select_one("span.a-icon-alt")
                if rating_element:
                    rating_match = re.search(r"(\d+\.\d+)", rating_element.text)
                    product["rating"] = rating_match.group(1) if rating_match else "N/A"
                else:
                    product["rating"] = "N/A"

                reviews_element = container.select_one(
                    "span.a-size-base.s-underline-text"
                )
                if reviews_element:
                    product["reviews_count"] = reviews_element.text.strip().replace(
                        ",", ""
                    )
                else:
                    product["reviews_count"] = "0"

                img_element = container.select_one("img.s-image")
                product["image_url"] = (
                    img_element["src"]
                    if img_element and "src" in img_element.attrs
                    else "N/A"
                )

                product["asin"] = container.get("data-asin", "N/A")

                products.append(product)
            except Exception as e:
                print(f"Error extracting product data: {e}")
                continue

        return products

    def search_amazon(self, keyword, num_pages=3):
        """
        Search Amazon for products using the given keyword and scrape multiple pages

        Args:
            keyword: The search keyword
            num_pages: Number of pages to scrape (default: 3)

        Returns:
            DataFrame: A pandas DataFrame containing product details
        """
        all_products = []

        try:
            self.driver = self._initialize_driver()

            if not self.driver:
                print("Failed to initialize driver. Exiting.")
                return pd.DataFrame()

            print(f"Navigating to Amazon homepage...")
            self.driver.get(self.base_url)
            self.human_like_delay()

            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "sp-cc-accept"))
                )
                cookie_button.click()
                print("Accepted cookies")
                self.human_like_delay()
            except (TimeoutException, NoSuchElementException):
                print("No cookie banner found or it wasn't clickable")

            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
                )
                search_box.clear()

                for char in keyword:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))

                self.human_like_delay()

                search_button = self.driver.find_element(
                    By.ID, "nav-search-submit-button"
                )
                search_button.click()

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error during search: {e}")
                if self.driver:
                    self.save_screenshot("search_error")
                return pd.DataFrame()

            self.human_like_delay()

            current_page = 1

            while current_page <= num_pages:
                print(f"Scraping page {current_page} of {num_pages}")

                self.save_screenshot(f"search_results_page{current_page}")

                for _ in range(random.randint(3, 5)):
                    self.human_like_scroll()

                page_source = self.driver.page_source
                html_file = self.save_html(current_page, page_source)
                print(f"Saved HTML to: {html_file}")

                products = self.extract_product_data(page_source)
                all_products.extend(products)

                print(f"Found {len(products)} products on page {current_page}")

                if current_page < num_pages:
                    try:
                        next_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(
                                (
                                    By.CSS_SELECTOR,
                                    ".s-pagination-item.s-pagination-next",
                                )
                            )
                        )

                        if "s-pagination-disabled" in next_button.get_attribute(
                            "class"
                        ):
                            print("Reached the last page")
                            break

                        next_button.click()
                        self.human_like_delay()
                        current_page += 1
                    except Exception as e:
                        print(f"Error navigating to next page: {e}")
                        break
                else:
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
            if self.driver:  # Only try to save screenshot if driver exists
                self.save_screenshot("error_screenshot")

        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    print("Browser closed successfully")
                except Exception as e:
                    print(f"Error closing browser: {e}")
                self.driver = None  # Set to None after quitting

        df = pd.DataFrame(all_products)
        return df

    def save_to_csv(self, df, keyword):
        """Save the scraped data to CSV"""
        if df.empty:
            print("No data to save")
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(
            self.output_dir, "csv", f"amazon_{keyword}_{timestamp}.csv"
        )

        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"Data saved to: {file_path}")

        return file_path

    def download_images(self, df):
        """Download product images to a folder"""
        if df.empty or "image_url" not in df.columns:
            print("No image URLs to download")
            return

        directory = os.path.join(self.output_dir, "images")

        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

        for i, row in df.iterrows():
            if pd.notna(row.get("image_url")) and row.get("image_url") != "N/A":
                try:
                    if pd.notna(row.get("title")):
                        safe_name = "".join(
                            c if c.isalnum() else "_" for c in row["title"]
                        )[:30]
                        filename = f"{directory}/product_{i}_{safe_name}.jpg"
                    else:
                        filename = f"{directory}/product_{i}.jpg"

                    urllib.request.urlretrieve(row["image_url"], filename)
                    print(f"Downloaded image {i+1}/{len(df)} to {filename}")
                except Exception as e:
                    print(f"Error downloading image {i+1}: {e}")


def main():

    keyword = input("Enter search keyword for Amazon: ").strip()

    try:
        num_pages = int(
            input("Enter number of pages to scrape (default: 3): ").strip() or "3"
        )
    except ValueError:
        num_pages = 3
        print("Invalid input. Using default: 3 pages")

    scraper = AmazonScraper()

    print(f"\nStarting Amazon scraper for '{keyword}'...")
    print(f"Will scrape {num_pages} pages of results")

    df = scraper.search_amazon(keyword, num_pages)

    if not df.empty:
        print(f"\nFound {len(df)} products")
        print("\nSample data:")
        print(df[["title", "price", "rating", "reviews_count"]].head())

        csv_path = scraper.save_to_csv(df, keyword)

        download_images = (
            input("\nDo you want to download product images? (y/n): ").lower() == "y"
        )
        if download_images:
            scraper.download_images(df)

        print(f"\nScraping completed successfully!")
        print(f"CSV data saved to: {csv_path}")
        print(f"HTML files saved to: {os.path.join(scraper.output_dir, 'html')}")

    else:
        print("\nNo products found or Amazon blocked the scraper.")
        print("Tips:")
        print("1. Check your internet connection")
        print("2. Try a different keyword")
        print("3. Use a VPN")
        print("4. Check the screenshots folder for debugging information")


if __name__ == "__main__":
    main()
