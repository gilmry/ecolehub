import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';
import { TestUsers } from './fixtures/test-data';

test.describe('Authentication Flow', () => {
  test('should load the login page', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();

    // Take initial screenshot for documentation
    await loginPage.takeScreenshot('01-login-page-loaded');

    await expect(page).toHaveTitle(/EcoleHub/);
    await expect(page.locator('h1')).toContainText('🏫 EcoleHub Stage 4');
  });

  test('should successfully login as parent', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();

    // Take screenshot before login
    await loginPage.takeScreenshot('02-before-parent-login');

    await loginPage.loginAsParent();

    // Verify successful login
    await dashboardPage.expectToBeDashboard();
    await dashboardPage.expectUserLoggedIn(TestUsers.parent.firstName, TestUsers.parent.lastName);

    // Take screenshot after successful login
    await dashboardPage.takeScreenshot('03-parent-logged-in-dashboard');
  });

  test('should successfully login as admin', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();

    await loginPage.loginAsAdmin();

    await dashboardPage.expectToBeDashboard();
    await dashboardPage.expectUserLoggedIn(TestUsers.admin.firstName, TestUsers.admin.lastName);

    // Take screenshot of admin dashboard
    await dashboardPage.takeScreenshot('04-admin-logged-in-dashboard');
  });

  test('should fail login with invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();

    // Try to login with invalid credentials
    await loginPage.login('invalid@email.com', 'wrongpassword');

    // Should show error message or stay on login page
    const isLoginFormVisible = await loginPage.loginForm.isVisible();
    const hasErrorMessage = await loginPage.errorMessage.isVisible();

    expect(isLoginFormVisible || hasErrorMessage).toBeTruthy();

    // Take screenshot of failed login
    await loginPage.takeScreenshot('05-failed-login-attempt');
  });

  test('should logout successfully', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    // Login first
    await page.goto('/');
    await loginPage.waitForLoadingToFinish();
    await loginPage.loginAsParent();
    await dashboardPage.expectToBeDashboard();

    // Take screenshot before logout
    await dashboardPage.takeScreenshot('06-before-logout');

    // Logout
    await dashboardPage.logout();

    // Should return to login page
    await loginPage.expectLoginFormVisible();

    // Take screenshot after logout
    await loginPage.takeScreenshot('07-after-logout');
  });
});