# Admin Panel

Modern React-based admin panel for the subscription microservice.

## Features

- **Dashboard**: Overview of key metrics (users, subscriptions, payments, revenue)
- **User Management**: View, search, activate/deactivate, verify, and update user roles
- **Subscription Management**: View and update subscription statuses
- **Payment Management**: View and update payment statuses
- **Invoice Management**: View all invoices
- **Plan Management**: Create, update, and delete subscription plans
- **Authentication**: Secure admin-only access with JWT tokens

## Tech Stack

- React 18 with TypeScript
- Vite for build tooling
- React Router for navigation
- Tailwind CSS for styling
- Axios for API calls
- Lucide React for icons

## Setup

1. Install dependencies:
```bash
cd admin-panel
npm install
```

2. Start development server:
```bash
npm run dev
```

The admin panel will be available at `http://localhost:3000`

3. Build for production:
```bash
npm run build
```

## API Configuration

The admin panel is configured to proxy API requests to `http://localhost:8000`. You can change this in `vite.config.ts`.

## Usage

1. Log in with an admin account
2. Navigate through different sections using the sidebar
3. Use search and filter options to find specific records
4. Click on actions to modify user/subscription/payment statuses

## Development

The panel uses:
- TypeScript for type safety
- Tailwind CSS for styling
- React Context for authentication state
- Protected routes for admin-only pages

