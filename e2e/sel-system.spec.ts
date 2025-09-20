import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';
import { SELServicesPage } from './pages/sel-services-page';
import { TestUsers, SELTestData } from './fixtures/test-data';

test.describe('SEL (Local Exchange System)', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();
    await loginPage.loginAsParent();
  });

  test('should display SEL balance on dashboard', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Check that SEL balance is visible
    await expect(dashboardPage.selBalance).toBeVisible();

    // Take screenshot of dashboard with balance
    await dashboardPage.takeScreenshot('08-sel-balance-displayed');
  });

  test('should navigate to SEL services page', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const selServicesPage = new SELServicesPage(page);

    await dashboardPage.expectToBeDashboard();

    // Navigate to services
    await dashboardPage.navigateToServices();

    // Verify we're on services page
    await selServicesPage.expectServicesPageVisible();

    // Take screenshot of services page
    await selServicesPage.takeScreenshot('09-sel-services-page');
  });

  test('should create a new SEL service', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const selServicesPage = new SELServicesPage(page);

    await dashboardPage.navigateToServices();
    await selServicesPage.expectServicesPageVisible();

    const newService = SELTestData.services[0];

    // Take screenshot before creating service
    await selServicesPage.takeScreenshot('10-before-creating-service');

    // Create new service
    await selServicesPage.createService(
      newService.title,
      newService.description,
      newService.category,
      newService.points
    );

    // Verify service was created
    await selServicesPage.expectServiceExists(newService.title);

    // Take screenshot after creating service
    await selServicesPage.takeScreenshot('11-after-creating-service');
  });

  test('should request a SEL service', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    const selServicesPage = new SELServicesPage(page);

    await dashboardPage.navigateToServices();
    await selServicesPage.expectServicesPageVisible();

    // First create a service to request
    const serviceToRequest = SELTestData.services[1];
    await selServicesPage.createService(
      serviceToRequest.title,
      serviceToRequest.description,
      serviceToRequest.category,
      serviceToRequest.points
    );

    // Take screenshot before requesting service
    await selServicesPage.takeScreenshot('12-before-requesting-service');

    // Request the service
    await selServicesPage.requestService(serviceToRequest.title);

    // Take screenshot after requesting service
    await selServicesPage.takeScreenshot('13-after-requesting-service');
  });

  test('should navigate between SEL tabs', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Test navigation between different tabs
    await dashboardPage.navigateToServices();
    await dashboardPage.takeScreenshot('14-services-tab');

    await dashboardPage.navigateToTransactions();
    await dashboardPage.takeScreenshot('15-transactions-tab');

    // Return to dashboard
    await dashboardPage.dashboardTab.click();
    await dashboardPage.waitForLoadingToFinish();
    await dashboardPage.takeScreenshot('16-back-to-dashboard');
  });
});