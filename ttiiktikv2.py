import undetected_chromedriver as uc
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import random
import os
import shutil
import base64
import json
import requests
from selenium.webdriver import ActionChains
import zipfile
import re
from urllib.parse import urlparse

# Add these imports for image processing
from PIL import Image
from io import BytesIO
import hashlib

def get_user_agent():
    """Return a realistic user agent string"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
    ]
    return random.choice(user_agents)
def create_proxy_extension(proxy):
    """
    Create a Chrome extension to use a proxy
    """
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """
    
    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
    );
    """ % (proxy['host'], proxy['port'], proxy['username'], proxy['password'])
    
    extension_path = os.path.join(os.getcwd(), 'proxy_extension')
    if not os.path.exists(extension_path):
        os.makedirs(extension_path)
    
    with open(os.path.join(extension_path, 'manifest.json'), 'w') as f:
        f.write(manifest_json)
    
    with open(os.path.join(extension_path, 'background.js'), 'w') as f:
        f.write(background_js)
    
    with zipfile.ZipFile(os.path.join(os.getcwd(), 'proxy_extension.zip'), 'w') as zp:
        zp.write(os.path.join(extension_path, 'manifest.json'), 'manifest.json')
        zp.write(os.path.join(extension_path, 'background.js'), 'background.js')
    
    return os.path.join(os.getcwd(), 'proxy_extension.zip')

def human_like_mouse_move(driver, element):
    """Move mouse to element in a human-like way with subtle curves"""
    action = ActionChains(driver)
    # Get the location of the element
    location = element.location
    size = element.size
    
    # Calculate target coordinates (center of the element)
    target_x = location['x'] + size['width'] / 2
    target_y = location['y'] + size['height'] / 2
    
    # Get current mouse position
    current_x = random.randint(0, driver.execute_script("return window.innerWidth;"))
    current_y = random.randint(0, driver.execute_script("return window.innerHeight;"))
    
    # Create a curve by generating points
    points = []
    # Generate a random bezier curve
    num_points = random.randint(5, 10)
    
    # Control points for bezier curve
    cp1_x = current_x + (target_x - current_x) * random.uniform(0.2, 0.4)
    cp1_y = current_y + (target_y - current_y) * random.uniform(0.2, 0.8)
    cp2_x = current_x + (target_x - current_x) * random.uniform(0.6, 0.8)
    cp2_y = current_y + (target_y - current_y) * random.uniform(0.2, 0.8)
    
    # Generate bezier curve points
    for i in range(num_points):
        t = i / (num_points - 1)
        # Cubic bezier curve formula
        x = (1-t)**3 * current_x + 3*(1-t)**2*t*cp1_x + 3*(1-t)*t**2*cp2_x + t**3*target_x
        y = (1-t)**3 * current_y + 3*(1-t)**2*t*cp1_y + 3*(1-t)*t**2*cp2_y + t**3*target_y
        points.append((int(x), int(y)))
    
    # Move through the curve with random delays
    for point in points:
        action.move_by_offset(point[0] - current_x, point[1] - current_y)
        current_x, current_y = point[0], point[1]
        # Random delay between movements
        time.sleep(random.uniform(0.01, 0.03))
    
    # Perform the action
    action.perform()
    time.sleep(random.uniform(0.1, 0.3))

def human_like_scroll(driver, distance=None, direction='down'):
    """Scroll in a humanlike way"""
    if distance is None:
        # If no distance specified, scroll a random amount
        distance = random.randint(300, 700)
    
    if direction == 'down':
        scroll_script = f"window.scrollBy({{top: {distance}, left: 0, behavior: 'smooth'}});"
    else:
        scroll_script = f"window.scrollBy({{top: -{distance}, left: 0, behavior: 'smooth'}});"
    
    driver.execute_script(scroll_script)
    # Random pause after scrolling
    time.sleep(random.uniform(0.5, 2.0))
    
    # Sometimes scroll back a bit to mimic human behavior
    if random.random() < 0.2:  # 20% chance
        small_scroll_back = random.randint(50, 100)
        if direction == 'down':
            back_script = f"window.scrollBy({{top: -{small_scroll_back}, left: 0, behavior: 'smooth'}});"
        else:
            back_script = f"window.scrollBy({{top: {small_scroll_back}, left: 0, behavior: 'smooth'}});"
        driver.execute_script(back_script)
        time.sleep(random.uniform(0.3, 0.7))

def add_fingerprinting_protection(driver):
    """Add script to modify navigator properties to avoid fingerprinting"""
    # Apply a random screen resolution
    width = random.randint(1280, 1920)
    height = random.randint(800, 1080)
    
    script = """
    // Modify navigator properties
    const originalNavigator = window.navigator;
    const modifiedNavigator = Object.create(originalNavigator);
    
    // Hardware concurrency (CPU cores)
    Object.defineProperty(modifiedNavigator, 'hardwareConcurrency', {
        get: () => %d
    });
    
    // Device memory
    Object.defineProperty(modifiedNavigator, 'deviceMemory', {
        get: () => %d
    });
    
    // Random platform
    Object.defineProperty(modifiedNavigator, 'platform', {
        get: () => "%s"
    });
    
    // Modify WebGL vendor and renderer
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
            return 'Google Inc.'; 
        }
        if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
            return 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)';
        }
        return getParameter.apply(this, arguments);
    };
    
    // Spoof screen resolution
    Object.defineProperty(window.screen, 'width', { get: () => %d });
    Object.defineProperty(window.screen, 'height', { get: () => %d });
    
    // Replace navigator
    Object.defineProperty(window, 'navigator', {
        get: () => modifiedNavigator
    });
    """ % (
        random.choice([2, 4, 6, 8]), 
        random.choice([2, 4, 8]),
        random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
        width,
        height
    )
    
    driver.execute_script(script)

def parse_count(count_str):
    """Convert TikTok count strings like '1.2M' to integers"""
    if not isinstance(count_str, str) or count_str == "N/A":
        return 0
        
    count_str = count_str.strip().lower()
    if 'k' in count_str:
        return int(float(count_str.replace('k', '')) * 1000)
    elif 'm' in count_str:
        return int(float(count_str.replace('m', '')) * 1000000)
    elif 'b' in count_str:
        return int(float(count_str.replace('b', '')) * 1000000000)
    else:
        try:
            return int(count_str)
        except:
            return 0

def analyze_results(df):
    """Analyze the scraped results"""
    if df.empty:
        return "No data found"
        
    # Convert counts to numeric for analysis
    for col in ['likes', 'comments', 'shares']:
        if col in df.columns:
            df[f'{col}_num'] = df[col].apply(parse_count)
    
    # Basic analysis
    analysis = {
        'total_videos': len(df),
        'avg_likes': df['likes_num'].mean() if 'likes_num' in df.columns else 'N/A',
        'avg_comments': df['comments_num'].mean() if 'comments_num' in df.columns else 'N/A',
        'avg_shares': df['shares_num'].mean() if 'shares_num' in df.columns else 'N/A',
    }
    
    # Add most popular video stats if available
    if 'likes_num' in df.columns and not df.empty:
        try:
            analysis['most_liked_video'] = df.loc[df['likes_num'].idxmax()]['url']
        except:
            analysis['most_liked_video'] = 'N/A'
    else:
        analysis['most_liked_video'] = 'N/A'
        
    if 'comments_num' in df.columns and not df.empty:
        try:
            analysis['most_commented_video'] = df.loc[df['comments_num'].idxmax()]['url']
        except:
            analysis['most_commented_video'] = 'N/A'
    else:
        analysis['most_commented_video'] = 'N/A'
        
    if 'shares_num' in df.columns and not df.empty:
        try:
            analysis['most_shared_video'] = df.loc[df['shares_num'].idxmax()]['url']
        except:
            analysis['most_shared_video'] = 'N/A'
    else:
        analysis['most_shared_video'] = 'N/A'
    
    return analysi

def save_image_from_element(driver, element, folder_path, prefix, idx):
    """Save an image from a WebElement or its children"""
    try:
        # First try to find an img element
        try:
            img_element = element.find_element(By.TAG_NAME, 'img')
        except:
            # If no direct img child, look for any img deeper in the structure
            try:
                img_element = element.find_element(By.XPATH, './/img')
            except:
                # If still no image, try to take a screenshot of the element itself
                return take_element_screenshot(driver, element, folder_path, prefix, idx)
        
        # Get the image source
        src = img_element.get_attribute('src')
        
        if src:
            if src.startswith('data:image'):
                # Handle base64 encoded images
                image_data = src.split(',')[1]
                image = Image.open(BytesIO(base64.b64decode(image_data)))
                file_path = os.path.join(folder_path, f"{prefix}_{idx}.png")
                image.save(file_path)
                return file_path
            else:
                # Handle URL images
                try:
                    # Add random user agent to avoid detection
                    headers = {
                        'User-Agent': get_user_agent(),
                        'Referer': driver.current_url
                    }
                    response = requests.get(src, headers=headers, stream=True)
                    if response.status_code == 200:
                        # Generate a unique filename based on URL
                        file_name = f"{prefix}_{idx}.jpg"
                        if 'content-type' in response.headers:
                            if 'png' in response.headers['content-type']:
                                file_name = f"{prefix}_{idx}.png"
                            elif 'gif' in response.headers['content-type']:
                                file_name = f"{prefix}_{idx}.gif"
                                
                        file_path = os.path.join(folder_path, file_name)
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        return file_path
                except Exception as e:
                    print(f"Error downloading image: {e}")
                    # If download fails, try screenshot
                    return take_element_screenshot(driver, element, folder_path, prefix, idx)
        
        # If we couldn't get an image, try taking a screenshot
        return take_element_screenshot(driver, element, folder_path, prefix, idx)
    
    except Exception as e:
        print(f"Error saving image: {e}")
        try:
            # Last resort: try to take a screenshot
            return take_element_screenshot(driver, element, folder_path, prefix, idx)
        except:
            return None

def take_element_screenshot(driver, element, folder_path, prefix, idx):
    """Take a screenshot of a specific element"""
    try:
        # Scroll element into view first
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
        time.sleep(0.5)  # Give time to scroll
        
        # Take screenshot of the element
        element_screenshot = element.screenshot_as_png
        image = Image.open(BytesIO(element_screenshot))
        file_path = os.path.join(folder_path, f"{prefix}_screenshot_{idx}.png")
        image.save(file_path)
        return file_path
    except Exception as e:
        print(f"Error taking element screenshot: {e}")
        return None

def extract_video_url(driver, element):
    """Try multiple methods to extract the actual video URL from a TikTok element"""
    video_url = None
    
    # Method 1: Direct video element
    try:
        video_elem = element.find_element(By.TAG_NAME, 'video')
        video_url = video_elem.get_attribute('src')
        if video_url:
            return video_url
    except:
        pass
    
    # Method 2: Look for video source elements
    try:
        source_elem = element.find_element(By.XPATH, './/source')
        video_url = source_elem.get_attribute('src')
        if video_url:
            return video_url
    except:
        pass
    
    # Method 3: Use JS to find the video URL
    try:
        video_url = driver.execute_script("""
            const element = arguments[0];
            // Check for video elements
            const videoEl = element.querySelector('video');
            if (videoEl && videoEl.src) return videoEl.src;
            
            // Check for source elements
            const sourceEl = element.querySelector('source');
            if (sourceEl && sourceEl.src) return sourceEl.src;
            
            // Look for any data attributes that might contain video URLs
            const allElements = element.querySelectorAll('*');
            for (const el of allElements) {
                for (const attr of el.attributes) {
                    if (attr.name.startsWith('data-') && 
                        typeof attr.value === 'string' &&
                        (attr.value.includes('.mp4') || attr.value.includes('video'))) {
                        return attr.value;
                    }
                }
            }
            
            return null;
        """, element)
        
        if video_url:
            return video_url
    except:
        pass
    
    return None

def extract_dom_data(driver, element):
    """Extract useful DOM data about the element for analysis"""
    try:
        dom_data = driver.execute_script("""
            const element = arguments[0];
            const data = {};
            
            // Basic element info
            data.tagName = element.tagName;
            data.id = element.id;
            data.className = element.className;
            
            // Size and position
            const rect = element.getBoundingClientRect();
            data.position = {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height
            };
            
            // Attributes
            data.attributes = {};
            for (const attr of element.attributes) {
                data.attributes[attr.name] = attr.value;
            }
            
            // Child elements summary
            data.childElementCount = element.childElementCount;
            data.children = Array.from(element.children).map(child => ({
                tagName: child.tagName,
                className: child.className,
                id: child.id
            }));
            
            // Check for video-specific elements
            data.hasVideoElement = !!element.querySelector('video');
            data.hasImageElement = !!element.querySelector('img');
            
            return data;
        """, element)
        
        return dom_data
    except Exception as e:
        print(f"Error extracting DOM data: {e}")
        return {}

def create_data_folder(hashtag):
    """Create a folder structure to store the scraped data"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    base_folder = os.path.join(os.getcwd(), f"tiktok_data_{hashtag}_{timestamp}")
    
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
        
    # Create subfolders for organization
    images_folder = os.path.join(base_folder, "images")
    videos_folder = os.path.join(base_folder, "videos")
    metadata_folder = os.path.join(base_folder, "metadata")
    debug_folder = os.path.join(base_folder, "debug")
    
    for folder in [images_folder, videos_folder, metadata_folder, debug_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            
    return {
        'base': base_folder,
        'images': images_folder,
        'videos': videos_folder,
        'metadata': metadata_folder,
        'debug': debug_folder
    }

def clean_filename(text):
    """Clean a string to make it suitable for a filename"""
    if not text:
        return "unknown"
    # Remove invalid filename characters
    cleaned = re.sub(r'[\\/*?:"<>|]', "", text)
    # Truncate if too long
    return cleaned[:50]  # Limit to 50 chars

def download_video(driver, video_url, folder_path, prefix):
    """Attempt to download a video from its URL"""
    if not video_url or not video_url.startswith('http'):
        return None
    
    try:
        # Add random user agent to avoid detection
        headers = {
            'User-Agent': get_user_agent(),
            'Referer': driver.current_url
        }
        
        response = requests.get(video_url, headers=headers, stream=True)
        if response.status_code == 200:
            # Generate a filename
            file_path = os.path.join(folder_path, f"{prefix}_video.mp4")
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024 * 1024):  # 1MB chunks
                    f.write(chunk)
            
            return file_path
    except Exception as e:
        print(f"Error downloading video: {e}")
    
    return None

def scrape_tiktok(hashtag, scroll_count=5, use_proxy=False):
    """
    Scrape TikTok videos based on hashtag and save comprehensive data
    
    Parameters:
    hashtag (str): Hashtag to search for without the # symbol
    scroll_count (int): Number of times to scroll down to load more content
    use_proxy (bool): Whether to use a proxy
    
    Returns:
    DataFrame: Pandas DataFrame containing scraped data
    """
    # Create folder structure for storing data
    folders = create_data_folder(hashtag)
    
    # Rest of the initialization code remains the same
    options = uc.ChromeOptions()
    
    # Add proxy if requested
    if use_proxy:
        # You would need to provide actual proxy details
        proxy = {
            'host': 'your_proxy_host',
            'port': 8080,
            'username': 'your_username',
            'password': 'your_password'
        }
        proxy_extension = create_proxy_extension(proxy)
        options.add_extension(proxy_extension)

    # Set a realistic user agent
    options.add_argument(f"--user-agent={get_user_agent()}")
    
    # Other options remain the same...
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    
    # Set window size to a common resolution with some randomization
    width = random.choice([1366, 1440, 1536, 1600, 1920])
    height = random.choice([768, 800, 864, 900, 1080])
    options.add_argument(f"--window-size={width},{height}")
    
    # Use custom user data directory to persist "human" browser data
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Other useful options
    options.add_argument("--lang=en-US,en;q=0.9")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    
    # Add preferences for downloading media
    prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": folders['videos'],
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Initialize the Chrome driver with our options
    driver = uc.Chrome(options=options)
    
    # Set geolocation to a random location
    latitude = random.uniform(25, 45)
    longitude = random.uniform(-120, -70)
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy": 100
    })
    
    # Apply fingerprinting protection
    add_fingerprinting_protection(driver)
    
    videos = []
    
    try:
        # First visit the TikTok homepage and interact with it a bit to seem more human
        driver.get("https://www.tiktok.com/")
        time.sleep(random.uniform(3, 5))
        
        # Save a screenshot of the homepage for debugging
        driver.save_screenshot(os.path.join(folders['debug'], "homepage.png"))
        
        # Perform some random scrolls on homepage
        for i in range(random.randint(1, 3)):
            human_like_scroll(driver)
        
        # Now navigate to the hashtag page
        url = f"https://www.tiktok.com/tag/{hashtag}"
        driver.get(url)
        
        # Random wait after page load
        time.sleep(random.uniform(3, 5))
        
        # Save a screenshot of the hashtag page for debugging
        driver.save_screenshot(os.path.join(folders['debug'], "hashtag_page.png"))
        
        # Save the page source for debugging
        with open(os.path.join(folders['debug'], "hashtag_page.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Accept cookies if prompted - try multiple different cookie banner selectors
        cookie_selectors = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Accept All')]",
            "//button[contains(@class, 'accept')]", 
            "//button[contains(text(), 'Agree')]",
            "//button[contains(@class, 'agree')]",
            "//div[contains(@class, 'cookie-banner')]//button"
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                human_like_mouse_move(driver, cookie_button)
                cookie_button.click()
                time.sleep(random.uniform(1, 2))
                break
            except:
                continue
        
        # Scroll to load more content with human-like behavior
        for i in range(scroll_count):
            # Random scroll distance
            human_like_scroll(driver)
            
            # Sometimes scroll back up a bit to simulate reading
            if random.random() < 0.3:  # 30% chance
                human_like_scroll(driver, random.randint(100, 300), direction='up')
            
            # Sometimes wait a bit longer to simulate reading content
            if random.random() < 0.2:  # 20% chance
                time.sleep(random.uniform(3, 7))
            
            # Take a screenshot after each scroll for debugging
            if i % 2 == 0:  # Every other scroll
                driver.save_screenshot(os.path.join(folders['debug'], f"scroll_{i}.png"))
        
        # Updated XPath selectors with even more variations for 2025 TikTok structure
        selectors = [
            "//div[contains(@class, 'video-feed-item')]",
            "//div[contains(@class, 'tiktok-x6y88p-DivItemContainer')]",
            "//div[contains(@data-e2e, 'challenge-item')]",
            "//div[@data-e2e='challenge-feed']/div",
            "//div[contains(@class, 'video-card')]",
            # Add more modern selectors
            "//div[contains(@class, 'tiktok-')]//a[contains(@href, '/video/')]/..",
            "//div[contains(@data-e2e, 'recommend-list-item')]",
            "//div[contains(@class, 'tiktok-')][@data-e2e='challenge-item']"
        ]
        
        print("Looking for video elements...")
        video_elements = []
        
        for selector in selectors:
            try:
                elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, selector))
                )
                if elements and len(elements) > 0:
                    video_elements = elements
                    print(f"Found {len(video_elements)} videos using selector: {selector}")
                    break
            except:
                continue
        
        if not video_elements:
            # If we couldn't find videos with XPath, try using JS to extract items
            try:
                # Use JavaScript to find video elements that might be hard to locate with XPath
                js_video_elements = driver.execute_script("""
                    // Try to find video elements by various means
                    const videos = [];
                    
                    // Method 1: Look for links to videos
                    const videoLinks = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                    videoLinks.forEach(link => {
                        // Get the parent container of each video link
                        let container = link;
                        for (let i = 0; i < 5; i++) {
                            container = container.parentElement;
                            if (container && container.querySelector('img') && container.offsetHeight > 100) {
                                videos.push(container);
                                break;
                            }
                        }
                    });
                    
                    // Method 2: Look for elements that appear like video containers
                    if (videos.length === 0) {
                        const possibleContainers = Array.from(document.querySelectorAll('div')).filter(div => {
                            return div.offsetHeight > 100 && 
                                  div.offsetWidth > 100 && 
                                  (div.querySelector('video') || div.querySelector('img')) &&
                                  div.querySelector('a');
                        });
                        videos.push(...possibleContainers);
                    }
                    
                    return videos;
                """)
                
                if js_video_elements and len(js_video_elements) > 0:
                    video_elements = js_video_elements
                    print(f"Found {len(video_elements)} videos using JavaScript")
            except Exception as e:
                print(f"JavaScript video detection failed: {e}")
        
        if not video_elements:
            # Take a screenshot if we couldn't find videos
            debug_screenshot = os.path.join(folders['debug'], f"tiktok_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            driver.save_screenshot(debug_screenshot)
            
            # Save page source for debugging
            debug_html = os.path.join(folders['debug'], f"tiktok_source_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            with open(debug_html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                
            print(f"Could not find any video elements. Saved screenshot to {debug_screenshot} and page source to {debug_html}")
        
        # Extract data from video elements with more flexible selectors
        for idx, video in enumerate(video_elements):
            try:
                print(f"Processing video {idx+1}/{len(video_elements)}...")
                
                # Create a unique ID for this video
                video_id = hashlib.md5(str(time.time() + idx).encode()).hexdigest()[:10]
                
                # Create a folder for this specific video
                video_folder = os.path.join(folders['base'], f"video_{video_id}")
                if not os.path.exists(video_folder):
                    os.makedirs(video_folder)
                
                # Scroll element into view with human-like behavior
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", video)
                time.sleep(random.uniform(0.5, 1.5))
                
                # Save screenshot of the video element
                element_screenshot = os.path.join(video_folder, f"video_element.png")
                try:
                    # Try to take a screenshot of the element
                    element_png = video.screenshot_as_png
                    with open(element_screenshot, "wb") as f:
                        f.write(element_png)
                except:
                    # If element screenshot fails, take full page screenshot
                    driver.save_screenshot(element_screenshot)
                
                # Extract DOM data and save it
                dom_data = extract_dom_data(driver, video)
                with open(os.path.join(video_folder, "dom_data.json"), "w", encoding="utf-8") as f:
                    json.dump(dom_data, f, indent=2)
                
                # Try different username selectors with JS fallback
                username = ""
                username_selectors = [
                    ".//a[contains(@class, 'author')]", 
                    ".//a[contains(@data-e2e, 'author')]",
                    ".//span[contains(@class, 'author')]",
                    ".//h3[contains(@class, 'author')]",
                    ".//a[contains(@href, '/@')]"
                ]
                
                for username_selector in username_selectors:
                    try:
                        username_elem = video.find_element(By.XPATH, username_selector)
                        username = username_elem.text
                        if username:
                            break
                    except:
                        pass
                
                # If XPath failed, try JavaScript
                if not username:
                    try:
                        username = driver.execute_script("""
                            const element = arguments[0];
                            
                            // Try to find author by href pattern
                            const authorLink = element.querySelector('a[href*="/@"]');
                            if (authorLink) return authorLink.textContent.trim();
                            
                            // Try to find by typical author class name patterns
                            const possibleAuthors = element.querySelectorAll('span, a, h3, div');
                            for (const el of possibleAuthors) {
                                if (el.textContent && 
                                   (el.textContent.startsWith('@') || 
                                    el.className.includes('author') || 
                                    el.className.includes('user'))) {
                                    return el.textContent.trim();
                                }
                            }
                            
                            return "";
                        """, video)
                    except:
                        pass
                
                # Try different description selectors with JS fallback
                description = ""
                desc_selectors = [
                    ".//div[contains(@class, 'desc')]",
                    ".//div[contains(@data-e2e, 'video-desc')]", 
                    ".//p[contains(@class, 'caption')]",
                    ".//div[contains(@class, 'caption')]",
                    ".//div[contains(@class, 'text')]"
                ]
                
                for desc_selector in desc_selectors:
                    try:
                        description_elem = video.find_element(By.XPATH, desc_selector)
                        description = description_elem.text
                        if description:
                            break
                    except:
                        pass
                
                # If XPath failed, try JavaScript
                if not description:
                    try:
                        description = driver.execute_script("""
                            const element = arguments[0];
                            
                            // Look for typical description elements
                            const possibleDescs = element.querySelectorAll('p, div, span');
                            for (const el of possibleDescs) {
                                if (el.textContent && 
                                   (el.className.includes('desc') || 
                                    el.className.includes('caption') || 
                                    el.className.includes('text'))) {
                                    return el.textContent.trim();
                                }
                            }
                            
                            // Alternative: Get the longest text element that's not the username
                            let longestText = "";
                            for (const el of possibleDescs) {
                                if (el.textContent && 
                                    el.textContent.trim().length > longestText.length && 
                                    !el.textContent.includes('@')) {
                                    longestText = el.textContent.trim();
                                }
                            }
                            return longestText;
                        """, video)
                    except:
                        pass
                
                # Get video URL with JS fallback
                video_url = ""
                url_selectors = [
                    ".//a[contains(@href, '/video/')]",
                    ".//a",
                    ".//div[contains(@class, 'item-video')]"
                ]
                
                for url_selector in url_selectors:
                    try:
                        url_elem = video.find_element(By.XPATH, url_selector)
                        video_url = url_elem.get_attribute("href")
                        if video_url and '/video/' in video_url:
                            break
                    except:
                        pass
                
                # If XPath failed, try JavaScript
                if not video_url or '/video/' not in video_url:
                    try:
                        video_url = driver.execute_script("""
                            const element = arguments[0];
                            
                            // Look for video links
                            const videoLink = element.querySelector('a[href*="/video/"]');
                            if (videoLink) return videoLink.href;
                            
                            // Try any link
                            const anyLink = element.querySelector('a');
                            return anyLink ? anyLink.href : "";
                        """, video)
                    except:
                        pass
                
                # Save any images found in the video element
                image_path = save_image_from_element(driver, video, video_folder, "thumbnail", idx)
                
                # Try to extract actual video content URL
                video_content_url = extract_video_url(driver, video)
                if video_content_url:
                    # Try to download the video
                    video_file_path = download_video(driver, video_content_url, video_folder, video_id)
                else:
                    video_file_path = None
                
                likes = comments = shares = "N/A"
                
                # If we found a video URL, visit it to get details
                detailed_metadata = {}
                video_page_screenshot = None
                
                if video_url and '/video/' in video_url:
                    try:
                        # Store current URL to return to later
                        current_url = driver.current_url
                        
                        # Visit video page
                        driver.get(video_url)
                        
                        # Wait for page to load with random delay
                        time.sleep(random.uniform(2, 4))
                        
                        # Save screenshot of the video page
                        video_page_screenshot = os.path.join(video_folder, "video_page.png")
                        driver.save_screenshot(video_page_screenshot)
                        
                        # Save HTML of the video page
                        with open(os.path.join(video_folder, "video_page.html"), "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        
                        # Try to save the full video if we couldn't earlier
                        if not video_file_path:
                            # Try to extract video from the video page
                            try:
                                video_elements = driver.find_elements(By.TAG_NAME, 'video')
                                if video_elements:
                                    video_content_url = video_elements[0].get_attribute('src')
                                    if video_content_url:
                                        video_file_path = download_video(driver, video_content_url, video_folder, video_id)
                            except Exception as e:
                                print(f"Error extracting video from page: {e}")
                        
                        # Scroll a bit on the video page
                        human_like_scroll(driver, random.randint(100, 300))
                        
                        # Extract more detailed metadata from the video page
                        try:
                            detailed_metadata = driver.execute_script("""
                                const metadata = {};
                                
                                // Get video publish date
                                const dateElements = document.querySelectorAll('time, span[contains(@class, "time")]');
                                for (const el of dateElements) {
                                    if (el.textContent && (el.textContent.includes('-') || el.textContent.includes('/'))) {
                                        metadata.publishDate = el.textContent.trim();
                                        break;
                                    }
                                }
                                
                                // Get music/sound info
                                const musicElements = document.querySelectorAll('h4, div, span');
                                for (const el of musicElements) {
                                    if (el.textContent && 
                                       (el.className.includes('music') || 
                                        el.className.includes('sound') ||
                                        el.className.includes('audio'))) {
                                        metadata.music = el.textContent.trim();
                                        break;
                                    }
                                }
                                
                                // Get hashtags
                                metadata.hashtags = Array.from(document.querySelectorAll('a[href*="/tag/"]'))
                                    .map(a => a.textContent.trim())
                                    .filter(t => t);
                                
                                // Get video dimensions if possible
                                const videoEl = document.querySelector('video');
                                if (videoEl) {
                                    metadata.videoDimensions = {
                                        width: videoEl.videoWidth,
                                        height: videoEl.videoHeight
                                    };
                                }
                                
                                return metadata;
                            """)
                            
                            # Save the detailed metadata
                            with open(os.path.join(video_folder, "detailed_metadata.json"), "w", encoding="utf-8") as f:
                                json.dump(detailed_metadata, f, indent=2)
                        except Exception as e:
                            print(f"Error extracting detailed metadata: {e}")
                        
                        # Try to get metrics with multiple selectors and JS fallback
                        metric_selectors = {
                            'likes': [
                                "//strong[contains(@data-e2e, 'like-count')]", 
                                "//span[contains(@data-e2e, 'like-count')]",
                                "//div[contains(@data-e2e, 'like-count')]",
                                "//span[contains(@class, 'like')]",
                                "//span[contains(@data-e2e, 'likes')]"
                            ],
                            'comments': [
                                "//strong[contains(@data-e2e, 'comment-count')]",
                                "//span[contains(@data-e2e, 'comment-count')]",
                                "//div[contains(@data-e2e, 'comment-count')]",
                                "//span[contains(@class, 'comment')]"
                            ],
                            'shares': [
                                "//strong[contains(@data-e2e, 'share-count')]",
                                "//span[contains(@data-e2e, 'share-count')]",
                                "//div[contains(@data-e2e, 'share-count')]",
                                "//span[contains(@class, 'share')]"
                            ]
                        }
                        
                        for metric, selectors in metric_selectors.items():
                            for selector in selectors:
                                try:
                                    value = driver.find_element(By.XPATH, selector).text
                                    if value:
                                        if metric == 'likes':
                                            likes = value
                                        elif metric == 'comments':
                                            comments = value
                                        else:
                                            shares = value
                                        break
                                except:
                                    continue
                        
                        # Go back to hashtag page with random wait
                        time.sleep(random.uniform(0.5, 1.5))
                        driver.get(current_url)
                        time.sleep(random.uniform(1.5, 3))
                    except Exception as e:
                        print(f"Error while visiting video page: {e}")
                        # Try to go back to hashtag page
                        try:
                            driver.get(url)
                            time.sleep(random.uniform(2, 4))
                        except:
                            pass
                
                # Create metadata for this video
                video_metadata = {
                    'video_id': video_id,
                    'username': username,
                    'description': description,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'url': video_url,
                    'image_path': image_path,
                    'video_path': video_file_path,
                    'detailed_metadata': detailed_metadata,
                    'scraped_date': datetime.datetime.now().isoformat(),
                    'hashtag': hashtag
                }
                
                # Save the metadata
                with open(os.path.join(video_folder, "metadata.json"), "w", encoding="utf-8") as f:
                    json.dump(video_metadata, f, indent=2)
                
                # Add to our results list
                videos.append(video_metadata)
                
                print(f"Successfully scraped video {idx+1}/{len(video_elements)}")
                
                # Random pause between videos to appear more human-like
                time.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                print(f"Error extracting data from video {idx+1}: {e}")
                continue
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if 'driver' in locals():
            # Take a final screenshot before quitting
            try:
                driver.save_screenshot(os.path.join(folders['debug'], f"final_state_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
            except:
                pass
            driver.quit()
    
    # Create DataFrame
    df = pd.DataFrame(videos)
    
    # Save the complete data to a CSV
    csv_path = os.path.join(folders['base'], f"tiktok_{hashtag}_data.csv")
    if not df.empty:
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    # Save a detailed summary report
    summary_path = os.path.join(folders['base'], "scraping_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"TikTok Scraper Summary Report\n")
        f.write(f"==========================\n\n")
        f.write(f"Hashtag: #{hashtag}\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total videos scraped: {len(videos)}\n")
        f.write(f"Data saved to: {folders['base']}\n\n")
        
        if videos:
            f.write(f"Sample of scraped videos:\n")
            for i, video in enumerate(videos[:5]):
                f.write(f"\n--- Video {i+1} ---\n")
                f.write(f"Username: {video.get('username', 'N/A')}\n")
                f.write(f"Likes: {video.get('likes', 'N/A')}\n")
                f.write(f"URL: {video.get('url', 'N/A')}\n")
                f.write(f"Images saved: {'Yes' if video.get('image_path') else 'No'}\n")
                f.write(f"Video saved: {'Yes' if video.get('video_path') else 'No'}\n")
    
    print(f"\nScraping completed! Data saved to {folders['base']}")
    return df, folders['base']

# The rest of the code (create_proxy_extension, get_user_agent, etc.) remains unchanged

if __name__ == "__main__":
    print("TikTok Scraper - Advanced Anti-Detection Edition with Media Saving")
    print("----------------------------------------------------------------")
    print("WARNING: TikTok actively blocks scrapers. This tool attempts to avoid detection,")
    print("but success cannot be guaranteed. Use responsibly and respect TikTok's ToS.")
    print("----------------------------------------------------------------")
    
    hashtag = input("Enter TikTok hashtag to scrape (without #): ").strip()
    scroll_count = int(input("Number of scrolls (more scrolls = more videos): ") or "5")
    
    use_proxy = input("Use proxy? (y/n, requires configuration): ").lower() == 'y'
    
    print(f"\nStarting to scrape TikTok for #{hashtag}...")
    results, data_folder = scrape_tiktok(hashtag, scroll_count, use_proxy=use_proxy)
    
    print(f"\nScraping completed! Scraped {len(results)} TikTok videos with hashtag #{hashtag}")
    print(f"All data saved to: {data_folder}")
    
    if not results.empty:
        print("\nSample of scraped data:")
        print(results[['username', 'likes', 'comments', 'shares']].head())
        
        # Analyze the results
        analysis = analyze_results(results)
        print("\nAnalysis:")
        for key, value in analysis.items():
            print(f"- {key.replace('_', ' ').title()}: {value}")
    else:
        print("\nNo videos were found. TikTok may have changed their page structure or blocked the scraper.")
        print(f"Check the debug files in {os.path.join(data_folder, 'debug')} for more information.")