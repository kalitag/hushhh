import asyncio
import logging
import re
import json
import random
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8327175937:AAGpC7M85iY-kbMVAcKJTrhXzKokWLGctCo"
BOT_USERNAME = "@Easy_uknowbot"

class ReviewCheckkBot:
    def __init__(self):
        self.session = None
        self.advanced_mode = False
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.platform_headers = {
            'meesho': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            },
            'amazon': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            'flipkart': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'X-User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
        }
        
        # Platform patterns
        self.platform_patterns = {
            'amazon': [r'amazon\.in', r'amzn\.to', r'amazon\.com'],
            'flipkart': [r'flipkart\.com', r'fkrt\.cc'],
            'meesho': [r'meesho\.com'],
            'myntra': [r'myntra\.com'],
            'ajio': [r'ajio\.com'],
            'snapdeal': [r'snapdeal\.com']
        }
        
        # URL shorteners
        self.shorteners = [
            'spoo.me', 'wishlink.com', 'cutt.ly', 'fkrt.cc', 
            'bitli.in', 'amzn.to', 'da.gd', 'bit.ly', 't.co'
        ]
        
        # Clothing keywords
        self.clothing_keywords = [
            'shirt', 'tshirt', 't-shirt', 'dress', 'kurti', 'saree', 'jeans', 
            'trouser', 'pant', 'shorts', 'skirt', 'top', 'blouse', 'jacket',
            'sweater', 'hoodie', 'suit', 'blazer', 'coat', 'leggings',
            'nightwear', 'innerwear', 'bra', 'panty', 'brief', 'boxer'
        ]
        
        # Brand cleanup words
        self.fluff_words = [
            'best', 'offer', 'deal', 'sale', 'new', 'latest', 'trending',
            'stylish', 'fashionable', 'premium', 'luxury', 'exclusive',
            'special', 'limited', 'hot', 'super', 'mega', 'great', 'amazing'
        ]

    async def init_session(self):
        """Initialize aiohttp session with enhanced settings"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=50, 
                limit_per_host=5,
                enable_cleanup_closed=True,
                keepalive_timeout=30
            )
            
            jar = aiohttp.CookieJar(unsafe=True)
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                cookie_jar=jar,
                trust_env=True
            )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    def get_random_headers(self, platform: str = None) -> Dict:
        """Get randomized headers for requests"""
        base_headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Add platform-specific headers
        if platform and platform in self.platform_headers:
            base_headers.update(self.platform_headers[platform])
        
        # Add random realistic headers
        if random.choice([True, False]):
            base_headers['Cache-Control'] = random.choice(['max-age=0', 'no-cache'])
        
        return base_headers

    def detect_platform(self, url: str) -> Optional[str]:
        """Detect platform from URL"""
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform
        return None

    def is_shortener(self, url: str) -> bool:
        """Check if URL is from a shortener service"""
        domain = urlparse(url).netloc.lower()
        return any(shortener in domain for shortener in self.shorteners)

    async def unshorten_url(self, url: str, max_redirects: int = 10) -> str:
        """Unshorten URL with enhanced redirect handling"""
        try:
            if not self.is_shortener(url):
                return self.clean_affiliate_params(url)
            
            await self.init_session()
            
            current_url = url
            redirect_count = 0
            
            while redirect_count < max_redirects:
                try:
                    headers = self.get_random_headers()
                    
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                    async with self.session.get(
                        current_url, 
                        headers=headers,
                        allow_redirects=False,
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as response:
                        
                        if response.status in [301, 302, 303, 307, 308]:
                            location = response.headers.get('Location')
                            if location:
                                current_url = location
                                redirect_count += 1
                                continue
                        
                        # Final URL found
                        final_url = str(response.url) if hasattr(response, 'url') else current_url
                        return self.clean_affiliate_params(final_url)
                        
                except Exception as e:
                    logger.warning(f"Redirect attempt {redirect_count} failed for {current_url}: {e}")
                    break
            
            return self.clean_affiliate_params(current_url)
                
        except Exception as e:
            logger.error(f"Error unshortening URL {url}: {e}")
            return url

    def clean_affiliate_params(self, url: str) -> str:
        """Remove affiliate and tracking parameters"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Parameters to remove
        remove_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'pid', 'af_', 'ref', 'tag', 'ascsubtag', 'pf_rd_', 'ie', 'qid',
            'sr', 'keywords', 'th', 'psc', 'linkCode', 'camp', 'creative',
            'creativeASIN', 'adid', 'crid', 'sprefix', 'dchild'
        ]
        
        # Clean query parameters
        clean_params = {}
        for key, value in query_params.items():
            if not any(remove_param in key.lower() for remove_param in remove_params):
                clean_params[key] = value
        
        # Rebuild URL
        clean_query = urlencode(clean_params, doseq=True)
        clean_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, clean_query, parsed.fragment
        ))
        
        return clean_url

    async def scrape_with_retry(self, url: str, platform: str, max_retries: int = 3) -> str:
        """Enhanced scraping with multiple retry strategies"""
        await self.init_session()
        
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers(platform)
                
                # Strategy variations per attempt
                if attempt == 1:
                    # Try with different user agent
                    headers['User-Agent'] = random.choice(self.user_agents)
                elif attempt == 2:
                    # Try with minimal headers
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': '*/*'
                    }
                
                if attempt > 0:
                    delay = random.uniform(2, 5) * attempt
                    await asyncio.sleep(delay)
                
                async with self.session.get(
                    url, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=25)
                ) as response:
                    
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 403:
                        logger.warning(f"403 error on attempt {attempt + 1} for {url}")
                        continue
                    elif response.status == 429:
                        # Rate limited - wait longer
                        await asyncio.sleep(random.uniform(5, 10))
                        continue
                    else:
                        logger.warning(f"HTTP {response.status} on attempt {attempt + 1} for {url}")
                        continue
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                continue
            except Exception as e:
                logger.warning(f"Error on attempt {attempt + 1} for {url}: {e}")
                continue
        
        raise Exception(f"Failed to scrape after {max_retries} attempts")

    async def scrape_product_details(self, url: str) -> Dict:
        """Scrape product details with enhanced error handling"""
        try:
            platform = self.detect_platform(url)
            if not platform:
                return {'error': 'Unsupported platform'}
            
            html = await self.scrape_with_retry(url, platform)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract details based on platform
            if platform == 'meesho':
                return await self.scrape_meesho(soup, url)
            elif platform == 'amazon':
                return await self.scrape_amazon(soup, url)
            elif platform == 'flipkart':
                return await self.scrape_flipkart(soup, url)
            elif platform == 'myntra':
                return await self.scrape_myntra(soup, url)
            elif platform == 'ajio':
                return await self.scrape_ajio(soup, url)
            elif platform == 'snapdeal':
                return await self.scrape_snapdeal(soup, url)
            else:
                return await self.scrape_generic(soup, url)
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {'error': 'Unable to extract product info'}

    async def scrape_meesho(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Meesho product details with enhanced selectors"""
        details = {'platform': 'meesho', 'url': url}
        
        title_selectors = [
            'h1[data-testid="product-title"]',
            'h1.sc-eDvSVe',
            'h1[class*="title"]',
            '[data-testid="product-title"]',
            '.product-title',
            'h1',
            '.sc-gKsewC',
            '[class*="ProductTitle"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                details['title'] = title_elem.get_text(strip=True)
                break
        
        price_selectors = [
            '[data-testid="product-price"]',
            '.sc-fubCfw',
            '.price',
            '[class*="price"]',
            '[class*="Price"]',
            '.sc-gKsewC span',
            'span[class*="rupee"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹?(\d+)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1)
                    break
        
        size_elements = soup.select('[data-testid="size-option"], .size-option, [class*="size"], [class*="Size"]')
        if size_elements:
            sizes = []
            for elem in size_elements:
                size_text = elem.get_text(strip=True)
                if size_text and len(size_text) <= 5 and size_text.replace('.', '').replace('-', '').isalnum():
                    sizes.append(size_text)
            
            if sizes:
                unique_sizes = list(dict.fromkeys(sizes))  # Remove duplicates
                if len(unique_sizes) >= 5:
                    details['sizes'] = 'All'
                else:
                    details['sizes'] = ', '.join(unique_sizes[:4])
        
        return details

    async def scrape_amazon(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Amazon product details"""
        details = {'platform': 'amazon', 'url': url}
        
        # Title extraction
        title_selectors = [
            '#productTitle',
            'h1.a-size-large',
            'h1 span',
            '.product-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
                break
        
        # Price extraction
        price_selectors = [
            '.a-price-whole',
            '.a-offscreen',
            '[data-asin-price]',
            '.a-price .a-offscreen'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹?(\d+)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1)
                    break
        
        return details

    async def scrape_flipkart(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Flipkart product details"""
        details = {'platform': 'flipkart', 'url': url}
        
        # Title extraction
        title_selectors = [
            'h1 span',
            '.B_NuCI',
            'h1',
            '.product-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
                break
        
        # Price extraction
        price_selectors = [
            '._30jeq3',
            '._1_WHN1',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹(\d+)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1)
                    break
        
        return details

    async def scrape_myntra(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Myntra product details"""
        details = {'platform': 'myntra', 'url': url}
        
        # Title extraction
        title_selectors = [
            'h1.pdp-title',
            '.pdp-name',
            'h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
                break
        
        # Price extraction
        price_selectors = [
            '.pdp-price strong',
            '.pdp-price',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹(\d+)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1)
                    break
        
        return details

    async def scrape_ajio(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Ajio product details"""
        details = {'platform': 'ajio', 'url': url}
        
        # Title extraction
        title_selectors = [
            'h1.prod-title',
            '.product-title',
            'h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
                break
        
        # Price extraction
        price_selectors = [
            '.prod-sp',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹(\d+)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1)
                    break
        
        return details

    async def scrape_snapdeal(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Snapdeal product details"""
        details = {'platform': 'snapdeal', 'url': url}
        
        # Title extraction
        title_selectors = [
            'h1[itemprop="name"]',
            '.pdp-product-name',
            'h1'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                details['title'] = title_elem.get_text(strip=True)
                break
        
        # Price extraction
        price_selectors = [
            '.payBlkBig',
            '[itemprop="price"]',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹(\d+)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1)
                    break
        
        return details

    async def scrape_generic(self, soup: BeautifulSoup, url: str) -> Dict:
        """Generic scraper for unknown platforms"""
        details = {'platform': 'generic', 'url': url}
        
        # Title extraction
        title_elem = soup.find('title')
        if title_elem:
            details['title'] = title_elem.get_text(strip=True)
        
        # Try to find price
        price_patterns = [r'₹(\d+)', r'Rs\.?\s*(\d+)', r'INR\s*(\d+)']
        text_content = soup.get_text()
        
        for pattern in price_patterns:
            price_match = re.search(pattern, text_content)
            if price_match:
                details['price'] = price_match.group(1)
                break
        
        return details

    def clean_title(self, title: str, platform: str) -> str:
        """Clean and format product title"""
        if not title:
            return ""
        
        # Remove extra whitespace and normalize
        title = ' '.join(title.split())
        
        # Remove common fluff words
        words = title.split()
        clean_words = []
        
        for word in words:
            if word.lower() not in self.fluff_words:
                clean_words.append(word)
        
        title = ' '.join(clean_words)
        
        # Detect if it's clothing
        is_clothing = any(keyword in title.lower() for keyword in self.clothing_keywords)
        
        # Extract brand (first word if it looks like a brand)
        words = title.split()
        brand = ""
        if words and len(words[0]) > 2 and words[0][0].isupper():
            brand = words[0]
        
        # Detect gender for clothing
        gender = ""
        if is_clothing:
            title_lower = title.lower()
            if any(word in title_lower for word in ['women', 'woman', 'girl', 'female', 'ladies']):
                gender = "Women"
            elif any(word in title_lower for word in ['men', 'man', 'boy', 'male', 'gents']):
                gender = "Men"
            elif any(word in title_lower for word in ['kid', 'child', 'baby']):
                gender = "Kids"
        
        # Format based on platform and type
        if platform == 'meesho' and is_clothing:
            if gender and brand:
                formatted = f"{brand} {gender} {' '.join(words[1:])}"
            elif gender:
                formatted = f"{gender} {title}"
            else:
                formatted = title
        else:
            if brand:
                formatted = f"{brand} {' '.join(words[1:])}"
            else:
                formatted = title
        
        # Limit to 8 words
        words = formatted.split()[:8]
        return ' '.join(words)

    def format_post(self, details: Dict, pin: str = "110001") -> str:
        """Format the final post according to ReviewCheckk style"""
        if 'error' in details:
            return f"❌ {details['error']}"
        
        platform = details.get('platform', '')
        title = details.get('title', '')
        price = details.get('price', '')
        url = details.get('url', '')
        sizes = details.get('sizes', '')
        
        if not title:
            return "❌ Unable to extract product info"
        
        # Clean title
        clean_title = self.clean_title(title, platform)
        if not clean_title:
            return "❌ Unable to extract product info"
        
        # Format price
        price_text = ""
        if price:
            if platform in ['amazon', 'flipkart', 'myntra', 'ajio', 'snapdeal']:
                price_text = f" from @{price} rs"
            else:
                price_text = f" @{price} rs"
        
        # Build post
        post_lines = []
        
        # Title and price line
        post_lines.append(f"{clean_title}{price_text}")
        
        # URL line
        post_lines.append(url)
        post_lines.append("")  # Blank line
        
        # Meesho specific additions
        if platform == 'meesho':
            if sizes:
                post_lines.append(f"Size - {sizes}")
            post_lines.append(f"Pin - {pin}")
            post_lines.append("")  # Blank line
        
        # End with channel tag
        post_lines.append("@reviewcheckk")
        
        return '\n'.join(post_lines)

    def extract_links_from_text(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\$$\$$,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls

    def extract_pin_from_text(self, text: str) -> str:
        """Extract pin code from text"""
        pin_pattern = r'\b(\d{6})\b'
        pin_match = re.search(pin_pattern, text)
        return pin_match.group(1) if pin_match else "110001"

    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process incoming message"""
        try:
            message = update.message
            if not message:
                return
            
            text = message.text or message.caption or ""
            
            # Extract URLs
            urls = self.extract_links_from_text(text)
            if not urls:
                return  # No URLs found, ignore message
            
            # Extract pin code
            pin = self.extract_pin_from_text(text)
            
            # Process each URL
            for url in urls:
                try:
                    # Add to processing queue
                    await self.processing_queue.put((message, url, pin))
                    
                    # Start processing if not already running
                    if not self.is_processing:
                        asyncio.create_task(self.process_queue())
                        
                except Exception as e:
                    logger.error(f"Error queuing URL {url}: {e}")
                    await message.reply_text("❌ Error processing link")
                    
        except Exception as e:
            logger.error(f"Error in process_message: {e}")

    async def process_queue(self):
        """Process the message queue"""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        try:
            while not self.processing_queue.empty():
                try:
                    message, url, pin = await asyncio.wait_for(
                        self.processing_queue.get(), timeout=1.0
                    )
                    
                    # Process the URL
                    await self.process_single_url(message, url, pin)
                    
                    # Small delay between processing
                    await asyncio.sleep(0.5)
                    
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    logger.error(f"Error processing queue item: {e}")
                    
        finally:
            self.is_processing = False

    async def process_single_url(self, message, url: str, pin: str):
        """Process a single URL with enhanced error handling"""
        try:
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
            # Unshorten URL
            clean_url = await self.unshorten_url(url)
            
            # Check if supported platform
            platform = self.detect_platform(clean_url)
            if not platform:
                await message.reply_text("❌ Unsupported or invalid product link")
                return
            
            # Scrape product details
            details = await self.scrape_product_details(clean_url)
            
            # Format post
            formatted_post = self.format_post(details, pin)
            
            # Send response
            await message.reply_text(formatted_post)
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await message.reply_text("❌ Unable to extract product info")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """🤖 ReviewCheckk Style Bot

Send me any product link and I'll format it in ReviewCheckk style!

Supported platforms:
• Amazon, Flipkart, Meesho
• Myntra, Ajio, Snapdeal
• URL shorteners (spoo.me, cutt.ly, etc.)

Commands:
/start - Show this message
/advancing - Enable advanced mode
/off_advancing - Disable advanced mode

Just send any product link and I'll handle the rest! 🚀"""
        
        await update.message.reply_text(welcome_text)

    async def advancing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable advanced mode"""
        self.advanced_mode = True
        await update.message.reply_text("✅ Advanced mode enabled! (Screenshots + Stock check)")

    async def off_advancing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable advanced mode"""
        self.advanced_mode = False
        await update.message.reply_text("✅ Advanced mode disabled! (Standard mode)")

def main():
    """Main function to run the bot"""
    # Create bot instance
    bot = ReviewCheckkBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("advancing", bot.advancing_command))
    application.add_handler(CommandHandler("off_advancing", bot.off_advancing_command))
    
    # Message handler for all text messages
    application.add_handler(MessageHandler(
        filters.TEXT | filters.CAPTION, 
        bot.process_message
    ))
    
    # Error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)
    
    # Cleanup on shutdown
    async def cleanup():
        await bot.close_session()
    
    application.add_handler(MessageHandler(filters.ALL, cleanup))
    
    # Start the bot
    logger.info("Starting ReviewCheckk Bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
