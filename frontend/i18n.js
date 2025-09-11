// EcoleHub Stage 4 - Simple i18n system for Vue 3
// Supports FR-BE (primary), NL-BE (Flemish), EN (international)

class EcoleHubI18n {
  constructor() {
    this.currentLocale = 'fr-BE';
    this.translations = {};
    this.fallbackLocale = 'fr-BE';
  }

  async loadLocale(locale) {
    try {
      const response = await fetch(`/locales/${locale}.json`);
      const translations = await response.json();
      this.translations[locale] = translations;
      return translations;
    } catch (error) {
      console.error(`Failed to load locale ${locale}:`, error);
      return {};
    }
  }

  async setLocale(locale) {
    if (!this.translations[locale]) {
      await this.loadLocale(locale);
    }
    
    this.currentLocale = locale;
    localStorage.setItem('ecolehub-locale', locale);
    
    // Update HTML lang attribute
    document.documentElement.lang = locale;
    
    return locale;
  }

  t(key, params = {}) {
    const keys = key.split('.');
    let translation = this.translations[this.currentLocale];
    
    // Navigate through nested keys
    for (const k of keys) {
      translation = translation?.[k];
    }

    // Fallback to primary locale if translation not found
    if (!translation && this.currentLocale !== this.fallbackLocale) {
      translation = this.translations[this.fallbackLocale];
      for (const k of keys) {
        translation = translation?.[k];
      }
    }

    // Return key if no translation found
    if (!translation) {
      // console.warn(`Translation missing for key: ${key} in locale: ${this.currentLocale}`);
      // Return a user-friendly fallback based on the key
      const keyParts = key.split('.');
      return keyParts[keyParts.length - 1].replace(/([A-Z])/g, ' $1').toLowerCase();
    }

    // Simple parameter replacement
    let result = translation;
    for (const [param, value] of Object.entries(params)) {
      result = result.replace(`{${param}}`, value);
    }

    return result;
  }

  getSupportedLocales() {
    return [
      { code: 'fr-BE', name: 'Français (Belgique)', flag: '🇧🇪' },
      { code: 'nl-BE', name: 'Nederlands (België)', flag: '🇳🇱' },
      { code: 'en', name: 'English', flag: '🇬🇧' }
    ];
  }

  getCurrentLocale() {
    return this.currentLocale;
  }

  async initializeFromStorage() {
    const stored = localStorage.getItem('ecolehub-locale') || 'fr-BE';
    
    // Load all locales at startup
    await Promise.all([
      this.loadLocale('fr-BE'),
      this.loadLocale('nl-BE'), 
      this.loadLocale('en')
    ]);
    
    await this.setLocale(stored);
  }
}

// Global i18n instance
const i18n = new EcoleHubI18n();

// Vue 3 plugin
const I18nPlugin = {
  install(app) {
    app.config.globalProperties.$t = (key, params) => i18n.t(key, params);
    app.config.globalProperties.$i18n = i18n;
    
    app.provide('i18n', i18n);
  }
};

// Export for use in main application
window.EcoleHubI18n = i18n;
window.I18nPlugin = I18nPlugin;