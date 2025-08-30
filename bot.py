from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import cv2
import pytesseract
import re

BOT_TOKEN = "8414049375:AAFMPUvB2u5KffNPsaAi3xu_DOiy-7dhHIg"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.text and "http" in message.text:
        url = message.text.strip()
        screenshot_path = capture_mobile_screenshot(url)
        title, price = extract_title_and_price(screenshot_path)
        caption = f"{title} @{price}rs"
        await message.reply_photo(photo=open(screenshot_path, 'rb'), caption=caption)

    elif message.photo:
        photo_file = await message.photo[-1].get_file()
        photo_path = "input.jpg"
        await photo_file.download_to_drive(photo_path)
        cleaned_path = clean_image(photo_path)
        title, price = extract_title_and_price(cleaned_path)
        caption = f"{title} @{price}rs"
        await message.reply_photo(photo=open(cleaned_path, 'rb'), caption=caption)

def capture_mobile_screenshot(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=720,1529")
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 Chrome/117.0.0.0 Mobile Safari/537.36")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    screenshot_path = "screenshot.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path

def clean_image(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    mask = cv2.bitwise_not(thresh)
    cleaned = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    cleaned_path = "cleaned.jpg"
    cv2.imwrite(cleaned_path, cleaned)
    return cleaned_path

def extract_title_and_price(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)

    title = ""
    prices = []

    for line in text.split('\n'):
        if any(currency in line for currency in ["₹", "Rs", "$", "€", "£"]):
            found = re.findall(r'\d+', line)
            prices.extend([int(p) for p in found])
        elif len(line.strip()) > 10 and not title:
            title = line.strip()

    final_price = min(prices) if prices else 0
    return title or "Product", final_price

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            })
        
        if platform and platform in self.platform_headers:
            base_headers.update(self.platform_headers[platform])
        
        if attempt == 1:
            base_headers['Cache-Control'] = 'no-cache'
            base_headers['Pragma'] = 'no-cache'
        elif attempt == 2:
            base_headers = {
                'User-Agent': user_agent,
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        elif attempt >= 3:
            base_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        
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

    async def unshorten_url(self, url: str, max_redirects: int = 15) -> str:
        """Enhanced URL unshortening with better redirect handling"""
        try:
            if not self.is_shortener(url):
                return self.clean_affiliate_params(url)
            
            await self.init_session()
            
            current_url = url
            redirect_count = 0
            visited_urls = set()
            
            while redirect_count < max_redirects:
                if current_url in visited_urls:
                    break
                visited_urls.add(current_url)
                
                try:
                    headers = self.get_random_headers(attempt=redirect_count)
                    
                    if redirect_count > 0:
                        await asyncio.sleep(random.uniform(1.0, 2.5))
                    
                    async with self.session.get(
                        current_url, 
                        headers=headers,
                        allow_redirects=False,
                        timeout=aiohttp.ClientTimeout(total=20)
                    ) as response:
                        
                        if response.status in [301, 302, 303, 307, 308]:
                            location = response.headers.get('Location')
                            if location:
                                if location.startswith('/'):
                                    parsed = urlparse(current_url)
                                    location = f"{parsed.scheme}://{parsed.netloc}{location}"
                                elif not location.startswith('http'):
                                    location = f"https://{location}"
                                
                                current_url = location
                                redirect_count += 1
                                continue
                        
                        final_url = str(response.url) if hasattr(response, 'url') else current_url
                        return self.clean_affiliate_params(final_url)
                        
                except Exception as e:
                    logger.warning(f"Redirect attempt {redirect_count} failed for {current_url}: {e}")
                    if redirect_count == 0:
                        return self.clean_affiliate_params(current_url)
                    break
            
            return self.clean_affiliate_params(current_url)
                
        except Exception as e:
            logger.error(f"Error unshortening URL {url}: {e}")
            return self.clean_affiliate_params(url)

    def clean_affiliate_params(self, url: str) -> str:
        """Remove affiliate and tracking parameters"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        remove_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'pid', 'af_', 'ref', 'tag', 'ascsubtag', 'pf_rd_', 'ie', 'qid',
            'sr', 'keywords', 'th', 'psc', 'linkCode', 'camp', 'creative',
            'creativeASIN', 'adid', 'crid', 'sprefix', 'dchild'
        ]
        
        clean_params = {}
        for key, value in query_params.items():
            if not any(remove_param in key.lower() for remove_param in remove_params):
                clean_params[key] = value
        
        clean_query = urlencode(clean_params, doseq=True)
        clean_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, clean_query, parsed.fragment
        ))
        
        return clean_url

    async def scrape_with_retry(self, url: str, platform: str, max_retries: int = 5) -> str:
        """Enhanced scraping with multiple sophisticated retry strategies"""
        await self.init_session()
        
        for attempt in range(max_retries):
            try:
                headers = self.get_random_headers(platform, attempt)
                
                if attempt > 0:
                    delay = min(random.uniform(2, 5) * (2 ** attempt), 30)
                    await asyncio.sleep(delay)
                
                timeout_duration = 30 + (attempt * 10)
                
                async with self.session.get(
                    url, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout_duration),
                    allow_redirects=True
                ) as response:
                    
                    if response.status == 200:
                        content = await response.text()
                        if len(content) > 1000:
                            return content
                        else:
                            logger.warning(f"Got minimal content on attempt {attempt + 1} for {url}")
                            continue
                    elif response.status == 403:
                        logger.warning(f"403 error on attempt {attempt + 1} for {url}")
                        continue
                    elif response.status == 429:
                        await asyncio.sleep(random.uniform(10, 20))
                        continue
                    elif response.status in [500, 502, 503, 504]:
                        await asyncio.sleep(random.uniform(5, 10))
                        continue
                    else:
                        logger.warning(f"HTTP {response.status} on attempt {attempt + 1} for {url}")
                        continue
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                continue
            except aiohttp.ClientError as e:
                logger.warning(f"Client error on attempt {attempt + 1} for {url}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error on attempt {attempt + 1} for {url}: {e}")
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
        """Enhanced Meesho scraper with more selectors"""
        details = {'platform': 'meesho', 'url': url}
        
        title_selectors = [
            'h1[data-testid="product-title"]',
            'h1.sc-eDvSVe',
            'h1[class*="title"]',
            '[data-testid="product-title"]',
            '.product-title',
            'h1',
            '.sc-gKsewC',
            '[class*="ProductTitle"]',
            '.sc-bczRLJ',
            '.sc-htpNat',
            'div[class*="title"] h1',
            'span[class*="title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                title_text = title_elem.get_text(strip=True)
                if len(title_text) > 5:
                    details['title'] = title_text
                    break
        
        price_selectors = [
            '[data-testid="product-price"]',
            '.sc-fubCfw',
            '.price',
            '[class*="price"]',
            '[class*="Price"]',
            '.sc-gKsewC span',
            'span[class*="rupee"]',
            '.sc-htpNat span',
            'div[class*="price"] span',
            'span[class*="₹"]'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'₹?(\d+(?:,\d+)*)', price_text.replace(',', ''))
                if price_match:
                    details['price'] = price_match.group(1).replace(',', '')
                    break
        
        size_elements = soup.select('[data-testid="size-option"], .size-option, [class*="size"], [class*="Size"], button[class*="size"]')
        if size_elements:
            sizes = []
            for elem in size_elements:
                size_text = elem.get_text(strip=True)
                if size_text and len(size_text) <= 6 and re.match(r'^[A-Z0-9\-\.]+$', size_text):
                    sizes.append(size_text)
            
            if sizes:
                unique_sizes = list(dict.fromkeys(sizes))
                if len(unique_sizes) >= 5:
                    details['sizes'] = 'All'
                else:
                    details['sizes'] = ', '.join(unique_sizes[:5])
        
        return details

    async def scrape_amazon(self, soup: BeautifulSoup, url: str) -> Dict:
        """Scrape Amazon product details"""
        details = {'platform': 'amazon', 'url': url}
        
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
        
        title_elem = soup.find('title')
        if title_elem:
            details['title'] = title_elem.get_text(strip=True)
        
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
        
        title = ' '.join(title.split())
        
        words = title.split()
        clean_words = []
        
        for word in words:
            if word.lower() not in self.fluff_words:
                clean_words.append(word)
        
        title = ' '.join(clean_words)
        
        is_clothing = any(keyword in title.lower() for keyword in self.clothing_keywords)
        
        words = title.split()
        brand = ""
        if words and len(words[0]) > 2 and words[0][0].isupper():
            brand = words[0]
        
        gender = ""
        if is_clothing:
            title_lower = title.lower()
            if any(word in title_lower for word in ['women', 'woman', 'girl', 'female', 'ladies']):
                gender = "Women"
            elif any(word in title_lower for word in ['men', 'man', 'boy', 'male', 'gents']):
                gender = "Men"
            elif any(word in title_lower for word in ['kid', 'child', 'baby']):
                gender = "Kids"
        
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
        
        words = formatted.split()[:8]
        return ' '.join(words)

    def format_post(self, details: Dict, pin: str = "110001") -> str:
        """Format the final post according to ReviewCheckk style"""
        if 'error' in details:
            return f"❌ {details['error']}\n\n@reviewcheckk"
        
        platform = details.get('platform', '')
        title = details.get('title', '')
        price = details.get('price', '')
        url = details.get('url', '')
        sizes = details.get('sizes', '')
        
        if not title:
            return "❌ Unable to extract product info\n\n@reviewcheckk"
        
        clean_title = self.clean_title(title, platform)
        if not clean_title:
            return "❌ Unable to extract product info\n\n@reviewcheckk"
        
        price_text = ""
        if price:
            if platform in ['amazon', 'flipkart', 'myntra', 'ajio', 'snapdeal']:
                price_text = f" from @{price} rs"
            else:
                price_text = f" @{price} rs"
        
        post_lines = []
        
        post_lines.append(f"{clean_title}{price_text}")
        
        post_lines.append(url)
        post_lines.append("")  # Blank line
        
        if platform == 'meesho':
            if sizes:
                post_lines.append(f"Size - {sizes}")
            post_lines.append(f"Pin - {pin}")
            post_lines.append("")  # Blank line
        
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
            
            urls = self.extract_links_from_text(text)
            if not urls:
                return
            
            pin = self.extract_pin_from_text(text)
            
            for url in urls:
                try:
                    await self.processing_queue.put((message, url, pin))
                    
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
                    
                    await self.process_single_url(message, url, pin)
                    
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
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            clean_url = await self.unshorten_url(url)
            
            platform = self.detect_platform(clean_url)
            if not platform:
                await message.reply_text("❌ Unsupported or invalid product link\n\n@reviewcheckk")
                return
            
            details = await self.scrape_product_details(clean_url)
            
            formatted_post = self.format_post(details, pin)
            
            await message.reply_text(formatted_post)
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await message.reply_text("❌ Unable to extract product info\n\n@reviewcheckk")

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
    bot = ReviewCheckkBot()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("advancing", bot.advancing_command))
    application.add_handler(CommandHandler("off_advancing", bot.off_advancing_command))
    
    application.add_handler(MessageHandler(
        filters.TEXT | filters.CAPTION, 
        bot.process_message
    ))
    
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)
    
    async def cleanup():
        await bot.close_session()
    
    application.add_handler(MessageHandler(filters.ALL, cleanup))
    
    logger.info("Starting ReviewCheckk Bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
