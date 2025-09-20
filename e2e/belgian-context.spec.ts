import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { DashboardPage } from './pages/dashboard-page';
import { BelgianClasses, SELTestData } from './fixtures/test-data';

test.describe('Belgian School Context', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);

    await page.goto('/');
    await loginPage.waitForLoadingToFinish();
    await loginPage.loginAsParent();
  });

  test('should display French interface by default', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Check for French text elements
    await expect(page.locator('h1')).toContainText('EcoleHub');

    // Take screenshot of French interface
    await dashboardPage.takeScreenshot('35-belgian-french-interface');

    // Check that typical French-Belgian terms are present
    const frenchElements = [
      'Tableau de bord',
      'Services SEL',
      'Transactions',
      'Messages',
      'Événements'
    ];

    for (const text of frenchElements) {
      await expect(page.locator(`text=${text}`)).toBeVisible();
    }
  });

  test('should handle Belgian school classes structure', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();
    await dashboardPage.navigateToProfile();

    // Take screenshot of profile page
    await dashboardPage.takeScreenshot('36-profile-with-belgian-classes');

    // Check if class selection includes Belgian classes
    const classSelect = page.locator('select[name*="class"], select[name*="classe"]');
    if (await classSelect.isVisible()) {
      const options = await classSelect.locator('option').allTextContents();

      // Check for Belgian maternelle classes
      const hasMaternelle = BelgianClasses.maternelle.some(cls =>
        options.some(option => option.includes(cls))
      );

      // Check for Belgian primaire classes
      const hasPrimaire = BelgianClasses.primaire.some(cls =>
        options.some(option => option.includes(cls))
      );

      expect(hasMaternelle || hasPrimaire).toBeTruthy();
    }
  });

  test('should use Belgian SEL rules and rates', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Check initial balance follows Belgian rules (120 units = 2 hours)
    const balanceText = await dashboardPage.selBalance.textContent();
    if (balanceText) {
      const balance = parseInt(balanceText.match(/\d+/)?.[0] || '0');

      // Balance should be within Belgian limits
      expect(balance).toBeGreaterThanOrEqual(SELTestData.minBalance);
      expect(balance).toBeLessThanOrEqual(SELTestData.maxBalance);
    }

    await dashboardPage.takeScreenshot('37-belgian-sel-balance');
  });

  test('should support Belgian localization features', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Check language selector
    const languageSelect = page.locator('#language-select');
    await expect(languageSelect).toBeVisible();

    // Take screenshot of language options
    await languageSelect.click();
    await dashboardPage.takeScreenshot('38-belgian-language-options');

    // Check for Belgian language options
    const options = await languageSelect.locator('option').allTextContents();
    const hasFrenchBelgian = options.some(option => option.includes('🇧🇪') || option.includes('fr-BE'));
    const hasDutchBelgian = options.some(option => option.includes('🇧🇪') || option.includes('nl-BE'));

    expect(hasFrenchBelgian || hasDutchBelgian).toBeTruthy();
  });

  test('should display Belgian-specific school information', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();

    // Check for Belgian school terminology
    const belgianTerms = [
      'maternelle',
      'primaire',
      'CEB',
      'école'
    ];

    await dashboardPage.takeScreenshot('39-belgian-school-context');

    // Check if any Belgian school terms are present
    let foundBelgianTerms = 0;
    for (const term of belgianTerms) {
      try {
        await expect(page.locator(`text=/${term}/i`)).toBeVisible({ timeout: 2000 });
        foundBelgianTerms++;
      } catch (error) {
        // Term not found, continue
      }
    }

    // At least some Belgian terms should be present
    expect(foundBelgianTerms).toBeGreaterThan(0);
  });

  test('should handle Belgian currency and time formats', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);

    await dashboardPage.expectToBeDashboard();
    await dashboardPage.navigateToTransactions();

    await dashboardPage.takeScreenshot('40-belgian-transactions-format');

    // Check for European time format (if any times are displayed)
    const timeElements = page.locator('text=/\\d{2}:\\d{2}/');
    if (await timeElements.count() > 0) {
      const timeText = await timeElements.first().textContent();
      // European format check (24-hour format)
      expect(timeText).toMatch(/^([01]?[0-9]|2[0-3]):[0-5][0-9]/);
    }

    // Check for SEL units display (Belgian style)
    const unitElements = page.locator('text=/unités?/i');
    if (await unitElements.count() > 0) {
      await expect(unitElements.first()).toBeVisible();
    }
  });
});