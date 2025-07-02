# LinkedIn Job Scraper

A comprehensive LinkedIn job scraping tool that extracts job postings data with intelligent parsing, LLM-enhanced skill extraction, and MongoDB storage. The system includes a browser extension for seamless job saving and a webhook server for real-time processing.

## 🌟 Features

- **Multi-mode Scraping**: Works with both authenticated and anonymous LinkedIn sessions
- **Smart Data Extraction**: Combines regex/NLP-based cheap extraction with OpenAI GPT for skill identification
- **Real-time Processing**: Webhook server with browser extension for one-click job saving
- **Data Storage**: MongoDB integration with automatic deduplication and indexing
- **Intelligent Parsing**: Extracts employment type, workplace type, salary, benefits, and location data
- **Currency Detection**: Automatically detects and normalizes currency codes based on location
- **Browser Extension**: Chrome extension for seamless job saving while browsing LinkedIn

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Browser Extension](#browser-extension)
  - [Webhook Server](#webhook-server)
  - [Jupyter Notebook](#jupyter-notebook)
- [Architecture](#architecture)
- [Data Structure](#data-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-job-scraper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome WebDriver**
   The system uses `webdriver-manager` to automatically download and manage ChromeDriver.

4. **Set up MongoDB**
   - Create a MongoDB Atlas account or set up a local MongoDB instance
   - Note your connection URI for configuration

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# LinkedIn Credentials (required for authenticated scraping)
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/

# OpenAI API (for LLM skill extraction)
OPENAI_API_KEY=your_openai_api_key
```

## 📖 Usage

### Command Line Interface

#### 1. Scrape Individual URLs
```bash
# Scrape specific job URLs
python main.py https://www.linkedin.com/jobs/view/1234567890/

# Scrape multiple URLs
python main.py \
  https://www.linkedin.com/jobs/view/1234567890/ \
  https://www.linkedin.com/jobs/search/?currentJobId=9876543210
```

#### 2. Batch Processing
```bash
# Add URLs to jobs_to_scrape.txt (one per line)
echo "https://www.linkedin.com/jobs/view/1234567890/" >> jobs_to_scrape.txt

# Run scraper
python main.py
```

#### 3. Test Single Job
```bash
python test.py
```

### Browser Extension

1. **Load the Extension**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `browser_extension` folder

2. **Start the Webhook Server**
   ```bash
   python webhook_server.py
   ```
   Server will run on `http://localhost:8000`

3. **Use the Extension**
   - Navigate to any LinkedIn job page
   - Click the extension icon
   - Click "Save this job" to add it to the processing queue
   - Monitor progress in the extension popup

### Webhook Server

The webhook server provides real-time job processing with a queue system:

```bash
python webhook_server.py
```

**Endpoints:**
- `POST /webhook` - Add job URL to processing queue
- `GET /status` - Get current processing statistics
- `GET /` - Health check

### Jupyter Notebook

Explore and analyze scraped data using the included Jupyter notebook:

```bash
jupyter notebook li_scraper.ipynb
```

## 🏗️ Architecture

### Core Components

1. **`main.py`** - CLI orchestrator for batch job scraping
2. **`scraper.py`** - Core scraping logic with Selenium WebDriver
3. **`db.py`** - MongoDB integration and data persistence
4. **`cheap_extract.py`** - Fast regex/NLP-based data extraction
5. **`llm_extract.py`** - OpenAI GPT-powered skill extraction
6. **`post_process.py`** - Data cleaning and normalization
7. **`webhook_server.py`** - Flask-based webhook server
8. **`site_converter.py`** - URL conversion utilities
9. **Browser Extension** - Chrome extension for seamless job saving

### Data Flow

```
LinkedIn URL → URL Conversion → Selenium Scraping → Cheap Extraction → 
LLM Enhancement → Post Processing → MongoDB Storage
```

### Extraction Pipeline

1. **Initial Scraping**: Uses `linkedin-scraper` library with Selenium
2. **Cheap Extraction**: Fast regex-based extraction of:
   - Employment type (full-time, part-time, contract, etc.)
   - Workplace type (remote, hybrid, on-site)
   - Degree requirements
   - Benefits
   - Basic skills
3. **LLM Enhancement**: OpenAI GPT extracts required skills if cheap extraction fails
4. **Post Processing**: 
   - Location parsing (city, province/state)
   - Date normalization
   - Salary currency detection
   - Seniority level inference

## 📊 Data Structure

Each job record contains:

```python
{
    "linkedin_url": "https://www.linkedin.com/jobs/view/1234567890/",
    "job_title": "Senior Data Scientist",
    "company": "TechCorp Inc.",
    "city": "Toronto",
    "province": "Ontario",
    "posted_at": datetime(2025, 1, 1),
    "applicant_count": 150,
    "employment_type": "full-time",
    "workplace_type": "hybrid",
    "seniority_level": "senior",
    "degree_required": "Bachelor",
    "currency_code": "CAD",
    "salary_min": 80000,
    "salary_max": 120000,
    "benefits": ["health benefits", "401(k)", "remote stipend"],
    "required_skills": ["Python", "SQL", "Machine Learning"],
    "job_description": "Full job description text...",
    "description_clean": "Truncated clean description...",
    "scraped_at": datetime(2025, 1, 1),
    "posting_age_days": 5
}
```

## 📦 Dependencies

- **Web Scraping**: `selenium`, `webdriver-manager`, `linkedin-scraper`
- **Data Processing**: `flashtext`, `dateparser`, `python-dotenv`
- **Database**: `pymongo`
- **AI/ML**: `openai`
- **Web Server**: `flask`
- **Development**: `jupyter`

## 🔧 Advanced Configuration

### WebDriver Settings
Modify `make_driver()` in `scraper.py` to customize browser behavior:
- Headless mode for production
- Custom user agents
- Proxy settings
- Browser arguments

### Extraction Customization
Edit keyword lists in `cheap_extract.py`:
- Add new employment types
- Expand benefits recognition
- Include industry-specific skills

### LLM Configuration
Adjust `llm_extract.py` settings:
- Change OpenAI model (currently uses `gpt-4.1-nano`)
- Modify system prompts
- Adjust temperature and timeout settings

## 🚨 Important Notes

- **Rate Limiting**: The scraper includes random delays (1.5-3.0 seconds) between requests
- **LinkedIn ToS**: Ensure compliance with LinkedIn's Terms of Service
- **Authentication**: Some features require LinkedIn login credentials
- **Resource Usage**: Headless mode recommended for production use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Users are responsible for ensuring compliance with LinkedIn's Terms of Service and applicable laws. Use responsibly and respect rate limits.