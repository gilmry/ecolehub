import { Page, Locator } from '@playwright/test';
import { BasePage } from '../utils/base-page';

export class DashboardPage extends BasePage {
  readonly header: Locator;
  readonly userInfo: Locator;
  readonly selBalance: Locator;
  readonly navigationTabs: Locator;
  readonly dashboardTab: Locator;
  readonly servicesTab: Locator;
  readonly transactionsTab: Locator;
  readonly messagesTab: Locator;
  readonly eventsTab: Locator;
  readonly shopTab: Locator;
  readonly profileTab: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);
    this.header = page.locator('header');
    this.userInfo = page.locator('text=/Connecté.*/ ');
    this.selBalance = page.locator('text=/💰.*unités/');
    this.navigationTabs = page.locator('.tab-navigation');
    this.dashboardTab = page.locator('button:has-text("🏠 Tableau de bord")');
    this.servicesTab = page.locator('button:has-text("🤝 Services SEL")');
    this.transactionsTab = page.locator('button:has-text("💳 Transactions")');
    this.messagesTab = page.locator('button:has-text("📝 Messages")');
    this.eventsTab = page.locator('button:has-text("📅 Événements")');
    this.shopTab = page.locator('button:has-text("🛍️ Boutique")');
    this.profileTab = page.locator('button:has-text("👤 Profil")');
    this.logoutButton = page.locator('button:has-text("Déconnexion")');
  }

  async expectToBeDashboard() {
    await this.expectToBeVisible(this.header);
    await this.expectToBeVisible(this.userInfo);
  }

  async expectUserLoggedIn(firstName: string, lastName: string) {
    await this.expectToContainText(this.userInfo, firstName);
    await this.expectToContainText(this.userInfo, lastName);
  }

  async expectSelBalance(balance: number) {
    await this.expectToContainText(this.selBalance, `${balance} unités`);
  }

  async navigateToServices() {
    await this.servicesTab.click();
    await this.waitForLoadingToFinish();
  }

  async navigateToTransactions() {
    await this.transactionsTab.click();
    await this.waitForLoadingToFinish();
  }

  async navigateToMessages() {
    await this.messagesTab.click();
    await this.waitForLoadingToFinish();
  }

  async navigateToEvents() {
    await this.eventsTab.click();
    await this.waitForLoadingToFinish();
  }

  async navigateToShop() {
    await this.shopTab.click();
    await this.waitForLoadingToFinish();
  }

  async navigateToProfile() {
    await this.profileTab.click();
    await this.waitForLoadingToFinish();
  }

  async logout() {
    await this.logoutButton.click();
    await this.waitForLoadingToFinish();
  }
}