# ReviewCheckk Style Telegram Bot

A production-ready Telegram bot that formats product links in the exact style of @reviewcheckk channel.

## Features

✅ **Multi-Platform Support**: Amazon, Flipkart, Meesho, Myntra, Ajio, Snapdeal  
✅ **URL Unshortening**: Handles spoo.me, cutt.ly, fkrt.cc, bitli.in, amzn.to, da.gd  
✅ **Smart Title Cleaning**: Brand-first formatting, gender detection, fluff removal  
✅ **Accurate Price Extraction**: Lowest price selection, proper formatting  
✅ **Meesho Special Features**: Size detection, pin code handling  
✅ **Anti-Detection**: Advanced headers, retry mechanisms  
✅ **Queue System**: Handles multiple links without hanging  
✅ **Error Recovery**: Robust error handling with user feedback  

## Quick Deploy to Railway

1. **Fork this repository**
2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your forked repository
3. **Set Environment Variables** (if needed):
   - Railway will automatically detect the Procfile
4. **Deploy**: Railway will automatically build and deploy

## Local Development

\`\`\`bash
# Clone repository
git clone <your-repo-url>
cd reviewcheckk-bot

# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
\`\`\`

## Bot Commands

- `/start` - Show welcome message and instructions
- `/advancing` - Enable advanced mode (screenshots + stock check)
- `/off_advancing` - Disable advanced mode

## Usage

Simply send any product link to the bot:

**Input**: `https://www.meesho.com/product/123456`

**Output**:
\`\`\`
Brand Women Kurti Set @799 rs
https://www.meesho.com/product/123456

Size - M, L, XL
Pin - 110001

@reviewcheckk
\`\`\`

## Supported Platforms

- **Amazon** (`amazon.in`, `amzn.to`)
- **Flipkart** (`flipkart.com`, `fkrt.cc`)
- **Meesho** (`meesho.com`)
- **Myntra** (`myntra.com`)
- **Ajio** (`ajio.com`)
- **Snapdeal** (`snapdeal.com`)

## URL Shorteners

- `spoo.me`
- `wishlink.com`
- `cutt.ly`
- `fkrt.cc`
- `bitli.in`
- `amzn.to`
- `da.gd`

## Technical Details

- **Framework**: python-telegram-bot v20+ (async)
- **Scraping**: aiohttp + BeautifulSoup4
- **Deployment**: Railway.com
- **Response Time**: < 3 seconds
- **Reliability**: Auto-restart, queue system, error recovery

## Configuration

The bot uses these default settings:
- **Bot Token**: Set in `bot.py`
- **Default Pin**: 110001 (for Meesho)
- **Max Title Words**: 8
- **Request Timeout**: 20 seconds

## Error Handling

- `❌ Unsupported or invalid product link` - Platform not supported
- `❌ Unable to extract product info` - Scraping failed
- `❌ Out of stock` - Product unavailable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use and modify!
\`\`\`

```text file=".gitignore"
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.DS_Store
*.log
