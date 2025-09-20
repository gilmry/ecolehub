import { Page, Locator } from '@playwright/test';
import { BasePage } from '../utils/base-page';

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly registerButton: Locator;
  readonly errorMessage: Locator;
  readonly loginForm: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.locator('#login-email');
    this.passwordInput = page.locator('#login-password');
    this.loginButton = page.locator('button:has-text("Se connecter")');
    this.registerButton = page.locator('button:has-text("S\'inscrire")');
    this.errorMessage = page.locator('.text-red-600');
    this.loginForm = page.locator('#login-form');
  }

  async login(email: string, password: string) {
    await this.fillField('#login-email', email);
    await this.fillField('#login-password', password);

    // Wait for login response
    const responsePromise = this.waitForApiResponse('/auth/token');
    await this.loginButton.click();

    try {
      await responsePromise;
      await this.waitForLoadingToFinish();
    } catch (error) {
      // Login might have failed, continue to let test verify
    }
  }

  async loginAsParent() {
    await this.login('parent@test.be', 'test123');
  }

  async loginAsAdmin() {
    await this.login('admin@test.be', 'admin123');
  }

  async loginAsDirection() {
    await this.login('direction@test.be', 'direction123');
  }

  async expectLoginFormVisible() {
    await this.expectToBeVisible(this.loginForm);
  }

  async expectErrorMessage(message: string) {
    await this.expectToContainText(this.errorMessage, message);
  }
}