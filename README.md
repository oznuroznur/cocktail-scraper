# IBA Cocktail Scraper

This script scrapes all cocktail recipes from the IBA website, including all paginated pages, and saves the Name, Ingredients, Method, Garnish, and URL for each cocktail into an Excel file.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure you have `chromedriver.exe` in your PATH or in the project root.

3. Run the scraper:
   ```bash
   python scraper/iba_cocktail_scraper.py
   ```

The output will be saved as `iba_cocktails.xlsx` in the current directory.

## Notes
- The script uses Selenium to handle dynamic content and pagination.
- Age verification is bypassed automatically.
- All cocktail details are scraped from their individual pages. 