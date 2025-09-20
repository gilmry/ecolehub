import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';
import { TestUsers } from './fixtures/test-data';

test.describe('Application Navigation', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();
    await loginPage.loginAsParent();
  });

  test('should navigate through all main sections', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Navigate through each main section
    const sections = [
      { name: 'Services', method: () => dashboardPage.navigateToServices(), screenshot: '17-services-section' },
      { name: 'Transactions', method: () => dashboardPage.navigateToTransactions(), screenshot: '18-transactions-section' },
      { name: 'Messages', method: () => dashboardPage.navigateToMessages(), screenshot: '19-messages-section' },
      { name: 'Events', method: () => dashboardPage.navigateToEvents(), screenshot: '20-events-section' },
      { name: 'Shop', method: () => dashboardPage.navigateToShop(), screenshot: '21-shop-section' },
      { name: 'Profile', method: () => dashboardPage.navigateToProfile(), screenshot: '22-profile-section' }
    ];

    for (const section of sections) {
      await section.method();
      await dashboardPage.takeScreenshot(section.screenshot);

      // Verify the section loaded (basic check)
      await expect(page.locator('body')).toBeVisible();
    }

    // Return to dashboard
    await dashboardPage.dashboardTab.click();
    await dashboardPage.waitForLoadingToFinish();
    await dashboardPage.takeScreenshot('23-final-dashboard-return');
  });

  test('should handle language switching', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Take screenshot in French (default)
    await dashboardPage.takeScreenshot('24-interface-french');

    // Switch to Dutch (if available)
    const languageSelect = page.locator('#language-select');
    if (await languageSelect.isVisible()) {
      await languageSelect.selectOption('nl-BE');
      await dashboardPage.waitForLoadingToFinish();
      await dashboardPage.takeScreenshot('25-interface-dutch');

      // Switch to English (if available)
      await languageSelect.selectOption('en');
      await dashboardPage.waitForLoadingToFinish();
      await dashboardPage.takeScreenshot('26-interface-english');

      // Switch back to French
      await languageSelect.selectOption('fr-BE');
      await dashboardPage.waitForLoadingToFinish();
      await dashboardPage.takeScreenshot('27-interface-back-to-french');
    }
  });

  test('should display privacy settings', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Click privacy settings button
    const privacyButton = page.locator('button:has-text("🔒")');
    if (await privacyButton.isVisible()) {
      await privacyButton.click();
      await dashboardPage.takeScreenshot('28-privacy-settings-opened');
    }
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await dashboardPage.expectToBeDashboard();
    await dashboardPage.takeScreenshot('29-mobile-dashboard');

    // Test navigation on mobile
    await dashboardPage.navigateToServices();
    await dashboardPage.takeScreenshot('30-mobile-services');

    await dashboardPage.navigateToMessages();
    await dashboardPage.takeScreenshot('31-mobile-messages');
  });

  test('should handle admin features for admin user', async ({ page }) => {
    // Logout and login as admin
    const dashboardPage = new DashboardPage(page);
    const loginPage = new LoginPage(page);

    await dashboardPage.logout();
    await loginPage.waitForLoadingToFinish();
    await loginPage.loginAsAdmin();

    await dashboardPage.expectToBeDashboard();
    await dashboardPage.expectUserLoggedIn(TestUsers.admin.firstName, TestUsers.admin.lastName);

    // Take screenshot of admin interface
    await dashboardPage.takeScreenshot('32-admin-interface');

    // Navigate through admin sections
    await dashboardPage.navigateToServices();
    await dashboardPage.takeScreenshot('33-admin-services');

    await dashboardPage.navigateToProfile();
    await dashboardPage.takeScreenshot('34-admin-profile');
  });
});