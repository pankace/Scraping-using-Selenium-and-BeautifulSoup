import undetected_chromedriver as uc
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import random
import os
from selenium.webdriver import ActionChains
import zipfile
import json

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
            scroll_script = f"window.scrollBy({{top: -{small_scroll_back}, left: 0, behavior: 'smooth'}});"
        else:
            scroll_script = f"window.scrollBy({{top: {small_scroll_back}, left: 0, behavior: 'smooth'}});"
        driver.execute_script(scroll_script)
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

def scrape_tiktok(hashtag, scroll_count=5, use_proxy=False):
    """
    Scrape TikTok videos based on hashtag
    
    Parameters:
    hashtag (str): Hashtag to search for without the # symbol
    scroll_count (int): Number of times to scroll down to load more content
    use_proxy (bool): Whether to use a proxy
    
    Returns:
    DataFrame: Pandas DataFrame containing scraped data
    """
    # Initialize Chrome options with advanced anti-detection settings
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
    
    # Disable automation flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Add standard options to make detection harder
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
        
        # Perform some random scrolls on homepage
        for i in range(random.randint(1, 3)):
            human_like_scroll(driver)
        
        # Now navigate to the hashtag page
        url = f"https://www.tiktok.com/tag/{hashtag}"
        driver.get(url)
        
        # Random wait after page load
        time.sleep(random.uniform(3, 5))
        
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
            driver.save_screenshot(f"tiktok_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            # Save page source for debugging
            with open(f"tiktok_source_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                
            print("Could not find any video elements. Saved screenshot and page source for debugging.")
        
        # Extract data from video elements with more flexible selectors
        for idx, video in enumerate(video_elements):
            try:
                # Scroll element into view with human-like behavior
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", video)
                time.sleep(random.uniform(0.5, 1.5))
                
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
                
                likes = comments = shares = "N/A"
                
                # If we found a video, visit it to get details but only sometimes (to avoid detection)
                if video_url and '/video/' in video_url and random.random() < 0.7:  # 70% chance to visit
                    try:
                        # Store current URL to return to later
                        current_url = driver.current_url
                        
                        # Visit video page
                        driver.get(video_url)
                        
                        # Wait for page to load with random delay
                        time.sleep(random.uniform(2, 4))
                        
                        # Scroll a bit on the video page
                        human_like_scroll(driver, random.randint(100, 300))
                        
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
                        
                        # JavaScript fallback for metrics
                        try:
                            metrics = driver.execute_script("""
                                // Try to find metrics by common patterns
                                const metrics = {};
                                
                                // Look for elements with numbers that might be metrics
                                const allElements = document.querySelectorAll('span, strong, div');
                                
                                // Patterns to look for 
                                const likePatterns = ['like', 'heart', 'favorite'];
                                const commentPatterns = ['comment', 'reply'];
                                const sharePatterns = ['share', 'forward'];
                                
                                for (const el of allElements) {
                                    const text = el.textContent.trim();
                                    // Skip if not a number or number with K/M/B
                                    if (!text.match(/^[\\d.,]+[KMBkmb]?$/)) continue;
                                    
                                    // Check element attributes and classes for hints
                                    const attributes = Array.from(el.attributes).map(attr => attr.name + ':' + attr.value).join(' ');
                                    
                                    if (likePatterns.some(p => attributes.toLowerCase().includes(p)) && !metrics.likes) {
                                        metrics.likes = text;
                                    } else if (commentPatterns.some(p => attributes.toLowerCase().includes(p)) && !metrics.comments) {
                                        metrics.comments = text;
                                    } else if (sharePatterns.some(p => attributes.toLowerCase().includes(p)) && !metrics.shares) {
                                        metrics.shares = text;
                                    }
                                }
                                
                                return metrics;
                            """)
                            if 'likes' in metrics and metrics['likes'] and likes == "N/A":
                                likes = metrics['likes']
                            if 'comments' in metrics and metrics['comments'] and comments == "N/A":
                                comments = metrics['comments']
                            if 'shares' in metrics and metrics['shares'] and shares == "N/A":
                                shares = metrics['shares']
                        except:
                            pass
                        
                        # If metrics still not found, look for numbers near typical icons
                        if likes == "N/A" or comments == "N/A" or shares == "N/A":
                            try:
                                driver.execute_script("""
                                    // Copy any found numbers to clipboard
                                    const temp = document.createElement('textarea');
                                    document.body.appendChild(temp);
                                    temp.value = Array.from(document.querySelectorAll('*')).map(
                                        e => e.textContent.trim()).filter(t => /^[\\d.,]+[KMBkmb]?$/.test(t)).join('|');
                                    temp.select();
                                    document.execCommand('copy');
                                    document.body.removeChild(temp);
                                """)
                            except:
                                pass
                        
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
                
                # Add the data to our results
                videos.append({
                    'username': username,
                    'description': description,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'url': video_url,
                    'scraped_date': datetime.datetime.now()
                })
                
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
                driver.save_screenshot(f"final_state_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            except:
                pass
            driver.quit()
    
    # Create DataFrame
    df = pd.DataFrame(videos)
    return df

# Rest of the code (parse_count, analyze_results) remains the same
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
        df[f'{col}_num'] = df[col].apply(parse_count)
    
    # Basic analysis
    analysis = {
        'total_videos': len(df),
        'avg_likes': df['likes_num'].mean(),
        'avg_comments': df['comments_num'].mean(),
        'avg_shares': df['shares_num'].mean(),
        'most_liked_video': df.loc[df['likes_num'].idxmax()]['url'] if not df.empty else 'N/A',
        'most_commented_video': df.loc[df['comments_num'].idxmax()]['url'] if not df.empty else 'N/A',
        'most_shared_video': df.loc[df['shares_num'].idxmax()]['url'] if not df.empty else 'N/A'
    }
    
    return analysis

if __name__ == "__main__":
    print("TikTok Scraper - Advanced Anti-Detection Edition")
    print("------------------------------------------------")
    print("WARNING: TikTok actively blocks scrapers. This tool attempts to avoid detection,")
    print("but success cannot be guaranteed. Use responsibly and respect TikTok's ToS.")
    print("------------------------------------------------")
    
    hashtag = input("Enter TikTok hashtag to scrape (without #): ").strip()
    scroll_count = int(input("Number of scrolls (more scrolls = more videos): ") or "5")
    
    use_proxy = input("Use proxy? (y/n, requires configuration): ").lower() == 'y'
    
    print(f"\nStarting to scrape TikTok for #{hashtag}...")
    results = scrape_tiktok(hashtag, scroll_count, use_proxy=use_proxy)
    
    # Save to CSV
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"tiktok_{hashtag}_{timestamp}.csv"
    results.to_csv(csv_filename, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
    
    print(f"\nScraping completed! Scraped {len(results)} TikTok videos with hashtag #{hashtag}")
    print(f"Results saved to {csv_filename}")
    
    if not results.empty:
        print("\nSample of scraped data:")
        print(results[['username', 'likes', 'comments', 'shares']].head())
        
        print("\nAnalysis:")
        analysis = analyze_results(results)
        for key, value in analysis.items():
            print(f"- {key.replace('_', ' ').title()}: {value}")
    else:
        print("\nNo videos were found. TikTok may have changed their page structure or blocked the scraper.")
        print("Try running with different options or check the website structure manually.")
        print("For advanced users: Check the saved screenshots and HTML source for debugging.")
