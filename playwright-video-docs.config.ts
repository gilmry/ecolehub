import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration optimized for video documentation generation
 * This config forces video recording for all tests to create documentation videos
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // Sequential execution for better video documentation
  forbidOnly: !!process.env.CI,
  retries: 0, // No retries for documentation videos
  workers: 1, // Single worker for consistent video generation
  timeout: 60000, // Longer timeout for documentation
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/video-docs-results.json' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost',
    trace: 'on', // Always generate traces for documentation
    video: 'on', // Always record videos
    screenshot: 'on', // Always take screenshots
    // Slower actions for better video documentation
    actionTimeout: 3000,
    navigationTimeout: 10000,
  },

  projects: [
    {
      name: 'documentation-chrome',
      use: {
        ...devices['Desktop Chrome'],
        // Optimize for documentation videos
        viewport: { width: 1280, height: 720 },
        // Slower animations for better video capture
        hasTouch: false,
        isMobile: false,
      },
    },
  ],

  webServer: {
    command: 'docker compose up -d && sleep 15',
    port: 80,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});