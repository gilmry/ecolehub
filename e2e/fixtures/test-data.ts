// Test user accounts based on the backend test fixtures
export const TestUsers = {
  parent: {
    email: 'parent@test.be',
    password: 'test123',
    firstName: 'Marie',
    lastName: 'Dupont',
    role: 'parent'
  },
  admin: {
    email: 'admin@test.be',
    password: 'admin123',
    firstName: 'Admin',
    lastName: 'System',
    role: 'admin'
  },
  direction: {
    email: 'direction@test.be',
    password: 'direction123',
    firstName: 'Jean',
    lastName: 'Direction',
    role: 'direction'
  }
};

// Belgian school classes for testing
export const BelgianClasses = {
  maternelle: ['M1', 'M2', 'M3'],
  primaire: ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
};

// SEL system test data
export const SELTestData = {
  services: [
    {
      title: 'Garde après école',
      description: 'Garde des enfants après les heures de classe',
      category: 'garde',
      points: 60
    },
    {
      title: 'Aide aux devoirs',
      description: 'Accompagnement scolaire personnalisé',
      category: 'education',
      points: 45
    },
    {
      title: 'Transport scolaire',
      description: 'Covoiturage pour aller à l\'école',
      category: 'transport',
      points: 30
    }
  ],
  initialBalance: 120,
  minBalance: -300,
  maxBalance: 600,
  standardRate: 60 // 1 hour = 60 units
};

// Test messages and events
export const TestContent = {
  messages: [
    {
      subject: 'Test de messagerie',
      content: 'Ceci est un message de test pour vérifier le système de messagerie.'
    }
  ],
  events: [
    {
      title: 'Réunion parents-professeurs',
      description: 'Rencontre trimestrielle avec les enseignants',
      date: '2024-12-15',
      time: '18:00'
    }
  ]
};

// API endpoints for testing
export const ApiEndpoints = {
  auth: {
    token: '/auth/token',
    me: '/auth/me',
    logout: '/auth/logout'
  },
  sel: {
    services: '/sel/services',
    transactions: '/sel/transactions',
    balance: '/sel/balance'
  },
  messages: '/messages',
  events: '/events',
  shop: '/shop',
  users: '/users'
};