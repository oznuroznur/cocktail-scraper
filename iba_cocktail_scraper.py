import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://iba-world.com/cocktails/all-cocktails/"

# Setup Selenium WebDriver
def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for headless mode
    return webdriver.Chrome(options=options)

# Bypass age verification
def bypass_age_verification(driver):
    driver.execute_script("localStorage.setItem('age_gate_confirm', '1');")
    driver.refresh()
    time.sleep(2)

# Get all paginated cocktail list page URLs
def get_all_list_pages(driver):
    driver.get(BASE_URL)
    bypass_age_verification(driver)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    pagination = soup.select_one(".iba-cocktails-pagination")
    pages = set([BASE_URL])
    if pagination:
        for a in pagination.find_all("a", class_="page-numbers"):
            href = a.get("href")
            if href:
                pages.add(href)
    return sorted(pages)

# Get all cocktail links from a list page
def get_cocktail_links_from_page(driver, page_url):
    driver.get(page_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = []
    for a in soup.select(".iba-cocktails-container .cocktail a"):
        href = a.get("href")
        if href and "/iba-cocktail/" in href:
            links.append(href)
    return links

def find_shortcode_after_heading(soup, heading_text):
    for heading in soup.find_all("h4"):
        if heading_text.lower() in heading.get_text(strip=True).lower():
            # Traverse siblings until we find the next .elementor-shortcode
            sibling = heading.parent.parent.find_next_sibling()
            while sibling:
                shortcode = sibling.find("div", class_="elementor-shortcode")
                if shortcode:
                    return shortcode
                sibling = sibling.find_next_sibling()
    return None



# Extract cocktail details from its page
def scrape_cocktail_detail(url):
    r = requests.get(url)
    s = BeautifulSoup(r.content, "html.parser")
    name = s.select_one("h2.cocktail-title, h1.elementor-heading-title")
    name = name.text.strip() if name else "No name"

    # Find each section reliably
    ingredients_div = find_shortcode_after_heading(s, "Ingredients")
    method_div = find_shortcode_after_heading(s, "Method")
    garnish_div = find_shortcode_after_heading(s, "Garnish")

    ingredients = "\n".join(li.get_text(strip=True) for li in ingredients_div.find_all("li")) if ingredients_div else ""
    method = method_div.get_text(separator="\n", strip=True) if method_div else ""
    garnish = garnish_div.get_text(strip=True) if garnish_div else ""

    return {
        "Name": name,
        "Ingredients": ingredients,
        "Method": method,
        "Garnish": garnish,
        "URL": url
    }

def main(output_file="iba_cocktails.xlsx"):
    driver = get_driver()
    try:
        print("🔎 Getting all paginated list pages...")
        list_pages = get_all_list_pages(driver)
        print(f"Found {len(list_pages)} pages.")
        all_links = set()
        for page_url in list_pages:
            print(f"➡️ Scanning: {page_url}")
            links = get_cocktail_links_from_page(driver, page_url)
            print(f"  {len(links)} cocktail links found.")
            all_links.update(links)
        print(f"Total unique cocktail links: {len(all_links)}")
        all_data = []
        for i, link in enumerate(sorted(all_links), 1):
            print(f"[{i}/{len(all_links)}] Scraping: {link}")
            try:
                data = scrape_cocktail_detail(link)
                all_data.append(data)
            except Exception as e:
                print(f"⚠️ Error scraping {link}: {e}")
            time.sleep(1)
        df = pd.DataFrame(all_data)
        df.to_excel(output_file, index=False)
        print(f"✅ Done! Data saved to {output_file}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 