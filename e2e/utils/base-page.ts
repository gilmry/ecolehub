import { Page, Locator, expect } from '@playwright/test';

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto(url: string) {
    await this.page.goto(url);
  }

  async waitForLoadingToFinish() {
    // Wait for Vue app to be ready - more flexible detection
    await this.page.waitForFunction(() => {
      // Check if Vue app is mounted and #app element exists
      const app = document.querySelector('#app');
      return app && (
        window.Vue ||
        app.classList.length > 0 ||
        app.children.length > 0 ||
        app.textContent?.trim()
      );
    }, { timeout: 15000 });

    // Additional wait for any network requests to settle
    await this.page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {
      // Ignore timeout, continue anyway
    });
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png`, fullPage: true });
  }

  async expectToBeVisible(locator: Locator) {
    await expect(locator).toBeVisible();
  }

  async expectToHaveText(locator: Locator, text: string) {
    await expect(locator).toHaveText(text);
  }

  async expectToContainText(locator: Locator, text: string) {
    await expect(locator).toContainText(text);
  }

  // Helper to wait for API requests
  async waitForApiResponse(urlPattern: string | RegExp) {
    return await this.page.waitForResponse(response =>
      typeof urlPattern === 'string'
        ? response.url().includes(urlPattern)
        : urlPattern.test(response.url())
    );
  }

  // Helper to fill form field
  async fillField(selector: string, value: string) {
    await this.page.fill(selector, value);
  }

  // Helper to click button and wait for navigation
  async clickAndWait(selector: string) {
    await Promise.all([
      this.page.waitForLoadState('networkidle'),
      this.page.click(selector)
    ]);
  }
}