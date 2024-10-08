from playwright.sync_api import sync_playwright

def youtube(text):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.youtube.com/")

    search = page.locator("input").first
    search.click()
    search.fill(text)
    search.press("Enter")
    
    page.locator("ytd-video-renderer").first.click()


def perplex(text):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.perplexity.ai/")
    
    search = page.get_by_placeholder("Ask anything...")
    search.click()
    search.fill(text)
    search.press("Enter")