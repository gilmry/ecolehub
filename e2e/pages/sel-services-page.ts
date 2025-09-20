import { Page, Locator } from '@playwright/test';
import { BasePage } from '../utils/base-page';

export class SELServicesPage extends BasePage {
  readonly servicesGrid: Locator;
  readonly createServiceButton: Locator;
  readonly serviceForm: Locator;
  readonly serviceTitleInput: Locator;
  readonly serviceDescriptionInput: Locator;
  readonly serviceCategorySelect: Locator;
  readonly servicePointsInput: Locator;
  readonly saveServiceButton: Locator;
  readonly cancelServiceButton: Locator;
  readonly serviceCards: Locator;

  constructor(page: Page) {
    super(page);
    this.servicesGrid = page.locator('.services-grid');
    this.createServiceButton = page.locator('button:has-text("Créer un service")');
    this.serviceForm = page.locator('#service-form');
    this.serviceTitleInput = page.locator('#service-title');
    this.serviceDescriptionInput = page.locator('#service-description');
    this.serviceCategorySelect = page.locator('#service-category');
    this.servicePointsInput = page.locator('#service-points');
    this.saveServiceButton = page.locator('button:has-text("Sauvegarder")');
    this.cancelServiceButton = page.locator('button:has-text("Annuler")');
    this.serviceCards = page.locator('.service-card');
  }

  async expectServicesPageVisible() {
    await this.expectToBeVisible(this.servicesGrid);
  }

  async createService(title: string, description: string, category: string, points: number) {
    await this.createServiceButton.click();
    await this.expectToBeVisible(this.serviceForm);

    await this.fillField('#service-title', title);
    await this.fillField('#service-description', description);
    await this.serviceCategorySelect.selectOption(category);
    await this.fillField('#service-points', points.toString());

    const responsePromise = this.waitForApiResponse('/sel/services');
    await this.saveServiceButton.click();

    try {
      await responsePromise;
      await this.waitForLoadingToFinish();
    } catch (error) {
      // Service creation might have failed, continue to let test verify
    }
  }

  async expectServiceExists(title: string) {
    const serviceCard = this.page.locator('.service-card', { hasText: title });
    await this.expectToBeVisible(serviceCard);
  }

  async expectServicesCount(count: number) {
    await this.page.waitForFunction(
      (expectedCount) => document.querySelectorAll('.service-card').length === expectedCount,
      count,
      { timeout: 5000 }
    );
  }

  async requestService(title: string) {
    const serviceCard = this.page.locator('.service-card', { hasText: title });
    const requestButton = serviceCard.locator('button:has-text("Demander")');

    const responsePromise = this.waitForApiResponse('/sel/transactions');
    await requestButton.click();

    try {
      await responsePromise;
      await this.waitForLoadingToFinish();
    } catch (error) {
      // Request might have failed, continue to let test verify
    }
  }
}