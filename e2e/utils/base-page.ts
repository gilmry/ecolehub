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
    // Wait for Vue app to be ready
    await this.page.waitForFunction(() => {
      return window.Vue && document.querySelector('#app')?.__vue_app__;
    }, { timeout: 10000 });
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