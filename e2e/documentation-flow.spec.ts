import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';
import { SELServicesPage } from './pages/sel-services-page';
import { TestUsers, SELTestData } from './fixtures/test-data';

/**
 * Special test suite designed for creating documentation videos
 * These tests include deliberate pauses and annotations for better video documentation
 */
test.describe('EcoleHub Documentation Flow', () => {
  test('Complete User Journey - Parent Workflow', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    const selServicesPage = new SELServicesPage(page);

    // === LOGIN PHASE ===
    await page.goto('/');
    await loginPage.waitForLoadingToFinish();

    // Pause for video documentation
    await page.waitForTimeout(2000);
    await loginPage.takeScreenshot('doc-01-welcome-page');

    // Show login process
    await loginPage.loginAsParent();
    await page.waitForTimeout(2000);

    // === DASHBOARD EXPLORATION ===
    await dashboardPage.expectToBeDashboard();
    await dashboardPage.expectUserLoggedIn(TestUsers.parent.firstName, TestUsers.parent.lastName);

    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-02-dashboard-overview');

    // Highlight SEL balance
    await dashboardPage.selBalance.hover();
    await page.waitForTimeout(1500);
    await dashboardPage.takeScreenshot('doc-03-sel-balance-highlighted');

    // === NAVIGATION DEMO ===
    // Show all main sections with pauses for documentation

    // Services Section
    await dashboardPage.navigateToServices();
    await page.waitForTimeout(2000);
    await selServicesPage.takeScreenshot('doc-04-services-section');

    // Create a service for documentation
    const demoService = SELTestData.services[0];
    await selServicesPage.createService(
      demoService.title,
      demoService.description,
      demoService.category,
      demoService.points
    );
    await page.waitForTimeout(2000);
    await selServicesPage.takeScreenshot('doc-05-service-created');

    // Transactions Section
    await dashboardPage.navigateToTransactions();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-06-transactions-section');

    // Messages Section
    await dashboardPage.navigateToMessages();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-07-messages-section');

    // Events Section
    await dashboardPage.navigateToEvents();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-08-events-section');

    // Shop Section
    await dashboardPage.navigateToShop();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-09-shop-section');

    // Profile Section
    await dashboardPage.navigateToProfile();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-10-profile-section');

    // === LANGUAGE SWITCHING DEMO ===
    // Show internationalization features
    const languageSelect = page.locator('#language-select');
    if (await languageSelect.isVisible()) {
      // Switch to Dutch
      await languageSelect.click();
      await page.waitForTimeout(1000);
      await languageSelect.selectOption('nl-BE');
      await page.waitForTimeout(2000);
      await dashboardPage.takeScreenshot('doc-11-dutch-interface');

      // Switch to English
      await languageSelect.selectOption('en');
      await page.waitForTimeout(2000);
      await dashboardPage.takeScreenshot('doc-12-english-interface');

      // Back to French
      await languageSelect.selectOption('fr-BE');
      await page.waitForTimeout(2000);
      await dashboardPage.takeScreenshot('doc-13-french-interface');
    }

    // === MOBILE RESPONSIVE DEMO ===
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-14-mobile-view');

    // Navigate in mobile view
    await dashboardPage.navigateToServices();
    await page.waitForTimeout(1500);
    await dashboardPage.takeScreenshot('doc-15-mobile-services');

    // Reset to desktop
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForTimeout(1000);

    // === LOGOUT DEMO ===
    await dashboardPage.logout();
    await page.waitForTimeout(2000);
    await loginPage.takeScreenshot('doc-16-logout-complete');
  });

  test('Admin Features Documentation', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    // === ADMIN LOGIN ===
    await page.goto('/');
    await loginPage.waitForLoadingToFinish();
    await page.waitForTimeout(2000);

    await loginPage.loginAsAdmin();
    await page.waitForTimeout(2000);

    await dashboardPage.expectToBeDashboard();
    await dashboardPage.expectUserLoggedIn(TestUsers.admin.firstName, TestUsers.admin.lastName);

    await dashboardPage.takeScreenshot('doc-17-admin-dashboard');

    // === ADMIN FEATURES TOUR ===
    // Show admin-specific features
    await dashboardPage.navigateToProfile();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-18-admin-profile');

    await dashboardPage.navigateToServices();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-19-admin-services');

    // Admin logout
    await dashboardPage.logout();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-20-admin-logout');
  });

  test('Belgian School Context Features', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();
    await loginPage.loginAsParent();

    await dashboardPage.expectToBeDashboard();
    await page.waitForTimeout(2000);

    // === BELGIAN FEATURES DEMO ===
    // Highlight Belgian-specific elements

    // Show SEL system (Belgian Local Exchange)
    await dashboardPage.selBalance.hover();
    await page.waitForTimeout(1500);
    await dashboardPage.takeScreenshot('doc-21-belgian-sel-system');

    // Show navigation to profile for Belgian classes
    await dashboardPage.navigateToProfile();
    await page.waitForTimeout(2000);
    await dashboardPage.takeScreenshot('doc-22-belgian-school-classes');

    // Final screenshot
    await dashboardPage.takeScreenshot('doc-23-belgian-context-complete');
  });
});