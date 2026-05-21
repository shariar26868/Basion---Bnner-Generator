# Basione Project Documentation

> This README contains the full Basione Client and Basione Server documentation for product reference and AI-assisted answers.

---

## Basione Client 🎨✨

Basione Client is a cutting-edge, AI-powered interactive banner design and e-commerce platform built with Next.js 15, TypeScript, Tailwind CSS v4, and Fabric.js. The platform empowers users to design, customize, and order high-quality physical banners through either an AI-driven layout generator or an advanced manual vector/canvas editor.

### 🌟 Key Features

1. 🎨 Advanced Interactive Canvas Editor
   - Powered by Fabric.js and managed seamlessly through the global `CanvasProvider.tsx`.
   - Rich Vector Editing: Layer management, custom image uploads, decorative elements, SVG/Sticker integration, and complete typography controls.
   - Precise Sizing & Auto Scaling: Custom specifications for length and width. Canvas boundaries auto-scale to ensure 100% accurate print preview ratios.
   - Smart History Stack: Fully supports multi-level Undo (Ctrl+Z) and Redo (Ctrl+Y) operations natively mapped in the toolbar.
   - Multi-Format Exporting: Seamlessly export vector canvas blueprints as high-resolution PNG, JPEG, WebP, or download the raw editable JSON canvas configuration.

2. ⚡ AI-Powered Banner Engine
   - Generates banner compositions based on natural language user prompts.
   - Connects seamlessly to AI backend endpoints to populate pre-aligned layouts in the editor automatically.

3. 🪙 Dynamic Pricing & VAT Engine
   - Dynamically evaluates area metrics in m² based on custom client-side inputs.
   - Calculates precise cost metrics including standard VAT (21% default) with responsive volume-discount tiers.

4. 🔒 Enterprise Authentication & Security
   - Fully integrated custom auth suite encompassing Sign In, Sign Up, Password Recovery, and OTP Verification routes under `(auth)`.
   - Secure JWT token preservation utilizing HTTP cookies with custom header auto-injection.

5. 📊 Dual Role Dashboard Ecosystem
   - Admin Dashboard: Central control center for handling platform parameters, managing users, template design catalogs, order transactions, FAQs, and marketing blogs.
   - User/Client Profile: Clean interface for customers to monitor active orders, download completed design invoice sheets, and customize their account settings.

### 🏗️ Technical Architecture & Directory Structure

```text
basione-client/
├── 📁 app/                           # Next.js App Router root layout and routing hierarchy
│   ├── 📁 (adminDashboard)/          # Admin-exclusive management views
│   ├── 📁 (auth)/                    # Sign-in, sign-up, password reset, and OTP verification flows
│   ├── 📁 (commonLayout)/            # Guest routes (landing page, FAQ templates, terms)
│   ├── 📁 (editor)/                  # Vector canvas designer screen & size selector
│   ├── 📁 (generate-banner)/         # AI prompt builder and generation interface
│   ├── 📁 (payment)/                 # Stripe/payment gateways & invoice templates
│   └── 📁 (userDashboard)/           # User profile layout and order details
├── 📁 components/                    # Reusable React components grouped by feature area
│   ├── 📁 landing/                   # Interactive home sections (Hero, Features, Gallery)
│   ├── 📁 ui/                        # Shadcn UI primitives (Button, Input, Accordion)
│   └── 📁 templates/                 # Custom design layout cards
├── 📁 features/                      # Domain-specific modules & UI shells
│   ├── 📁 editor/                    # Interactive elements for the canvas toolbar & menus
│   └── 📁 auth/                      # Core auth panels
├── 📁 providers/                     # React Context and Redux state provider mounts
│   ├── [CanvasProvider.tsx](file:///c:/Projects/basione-client/providers/CanvasProvider.tsx)     # FabricJS viewport controller & event handler suite
│   └── [Provider.tsx](file:///c:/Projects/basione-client/redux/Provider.tsx)           # Redux Toolkit global store wrapper
├── 📁 redux/                         # State Management layer via Redux Toolkit & RTK Query
│   ├── 📁 api/                       # API Slices (baseApi, authApi, bannerApi, orderApi)
│   ├── 📁 features/                  # Local synchronous slices (e.g., user slice)
│   └── [store.ts](file:///c:/Projects/basione-client/redux/store.ts)               # Persisted store configurations
├── 📁 lib/                           # Utility scripts and shared helpers
│   ├── [canvasize.ts](file:///c:/Projects/basione-client/lib/canvasize.ts)           # Dynamic coordinate scaler
│   └── [utils.ts](file:///c:/Projects/basione-client/lib/utils.ts)               # Base64-to-File converting & tailwind-merge helper
└── ⚙️ Config files                   # Next.js, PostCSS, Tailwind CSS v4, TypeScript, package.json
```

### 🛠️ Technology Stack

| Technology | Purpose | Description |
|------------|---------|-------------|
| Next.js 15 (App Router) | Core Framework | Production-ready React framework offering SSR, layouts, and route groups. |
| Fabric.js | Interactive Canvas | Vector rendering, text manipulation, and complex element transformations. |
| Redux Toolkit & RTK Query | State & API | Caching, synchronized request handling, and persistent user profile caching. |
| Tailwind CSS v4 | UI Styling | Premium modern design utilizing glassmorphism, responsive utility bindings, and HSL palettes. |
| Framer Motion | Micro-Animations | Smooth transitions and state-based responsive movements. |
| Zod & React Hook Form | Input Validation | Fully typed schemas protecting form inputs across the checkout and sign-in streams. |
| Leaflet & Google Maps | Geospatial Services | Address matching and service map routing for deliveries. |

### ⚡ Development & Getting Started

#### Prerequisites

Make sure you have Node.js installed (v18+ recommended) and a package manager like npm, yarn, or pnpm.

#### Installation

```bash
git clone https://github.com/Tahsin0909/basione-client.git
cd basione-client
npm install
```

#### Configure Environment Variables

Create a `.env` or `.env.local` file at the project root directory and define the backend API endpoints:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/v1
```

#### Launch Local Development

```bash
npm run dev
```

Open `http://localhost:3000` to view the application.

#### Production Build & Verification

```bash
npm run type-check
npm run build
```

### 🧩 Architectural Highlights & Custom Patterns

- **The Canvas State System**: All interactive actions in the editor are governed by `CanvasProvider.tsx`. It synchronizes Fabric.js changes back into memory using lightweight listeners, exposing modular callbacks such as `undo`, `redo`, `saveDesign`, and `exportAndDownload` down the component tree.
- **Auto-Optimized Client Storage**: To minimize payload loads on external databases, large active templates and uploaded user imagery are saved safely in the browser's persistent sandbox using IndexedDB helpers like `saveUploadedImageToIndexedDb.ts`.

---

## Basione Server

Basione Server is a premium, production-ready e-commerce RESTful API backend designed for the Basione banner printing platform.

The server is built with a state-of-the-art Node.js, Express, TypeScript, Prisma ORM, and MongoDB architecture. It implements dynamic AI banner variant generation, double payment integrations (Stripe + Mollie), asynchronous processing queues (BullMQ), comprehensive admin panel management, a rich content blog system, decoration categories, and a premium unified aggregation layer.

### 🚀 Key Features

- **AI Banner Generation:** Connects to dynamic AI engines to generate distinct banner variants based on user inputs (occasions, styles, descriptions) with automatic pricing calculation.
- **Dual Payment Integrations:** Dual processing support via Mollie (ideal for European markets like iDEAL) and Stripe with secure webhook synchronizations.
- **Asynchronous Job Processing (BullMQ):** Fully decoupled task queues for transactional email delivery, AI chat pipelines, database cleanups, and high-volume background tasks backed by Redis.
- **Flexible Aggregation Layer:** A high-performance parallelized data aggregation endpoint (`/api/v1/aggregate`) that merges public catalogs (banners, blogs, decorations, FAQs) and optional authenticated user profiles/orders in a single parallel query (`Promise.all`).
- **Secure Administration Interface:** Deep order lifecycle control (pending, processing, ready, shipped, delivered, cancelled, refunded) with automatic transactional customer notification emails.
- **Rich Blog System:** Full publishing workflows with automated slug generation, cover image upload, tags, draft status, and category sorting.

### 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| Runtime & Language | Node.js, TypeScript, TS-Node-Dev |
| Web Server Framework | Express v5.x (High performance, minimalist) |
| Database & ORM | MongoDB Atlas, Prisma ORM (Type-safe schemas) |
| Authentication & Security | JSON Web Tokens (JWT), Cookies, Bcrypt hashing |
| Payment Gateways | Mollie API, Stripe API, secure automated webhooks |
| Queue & Job Runners | BullMQ, Redis (ioredis) |
| Cloud File Storage | Amazon S3 (AWS SDK v3), Cloudinary (Image management) |
| Automated Emails | Nodemailer (HTML templates, custom SMTP) |
| Validation Layer | Zod (Runtime JSON schema validation) |
| Build & Deployments | TypeScript compiler (tsc), Vercel edge deployment |

### 📁 Project Directory Structure

```text
src/
├── app/
│   ├── bullMQ/
│   │   ├── queues/          # BullMQ queue definitions (mail, order, AI chat, etc.)
│   │   └── workers/         # Redis job workers (mail processor)
│   ├── db/                  # DB bootstrap connection & admin seeding
│   ├── error/               # Centralized global error handling classes (AppError)
│   ├── lib/                 # Third-party client singletons (Prisma, Redis, Stripe, Mollie, Cloudinary)
│   ├── middleware/          # Security, token checking, validation, multer uploads
│   ├── modules/             # Modulized Feature Layers
│   │   ├── admin/           # Admin panel operations (users, orders, dashboards, FAQs, templates)
│   │   ├── aggregate/       # Unified public and user data aggregator
│   │   ├── auth/            # Standard session authentication & tokens
│   │   ├── banner/          # AI banners & templates generation
│   │   ├── blog/            # Dynamic blogging engine
│   │   ├── decorations/     # Catalog decoration items & categories
│   │   ├── invoice/         # PDF receipt/invoice creation (PDFKit)
│   │   ├── order/           # Order creation & cancel flow
│   │   ├── payment/         # Mollie transaction handler
│   │   └── stripe/          # Stripe transaction processing
│   ├── routes/              # Centralized route index & module attachment
│   └── utils/               # Formatting, verification, layout calculations, and email templates
├── config/                  # Configuration loaders (JWT, port, credentials)
├── app.ts                   # Express server config and error routing
└── server.ts                # App entrypoint
prisma/
└── schema.prisma            # Prisma MongoDB database schema definition
```

### 🗄️ Database Schema Models

The database is built on MongoDB using Prisma ORM. Key database models are:

- **User:** Represents registration data, roles (user, admin), account verification (OTPs), custom profile pictures, and addresses.
- **Banner:** The core banner designs. Can be saved as user-created banners or global templates (`isTemplate: true`) containing dimensions, occasion, styles, AI prompt history, and price calculations.
- **Order:** Links User and Banner for sales. Details exact banner sizes, quantity, VAT breakdowns (21%), delivery details (standard, express delivery, pickups), tracking numbers, and delivery statuses.
- **Invoice:** PDF invoice receipts generated upon successful payments (using PDFKit), uploaded to S3, and emailed to customers automatically.
- **Payment:** Links transactions to specific orders with complete raw payload responses from Stripe/Mollie hooks.
- **Address:** Houses precise billing/shipping addresses mapped specifically per order.
- **Decoration & DecorationCategory:** Contains catalog details of additional party decorations available to users.
- **Faq:** Houses categorized frequently asked questions displayed in the public frontend help desk.
- **Blog:** Contains articles for marketing, including unique slug lines, draft/publish status, cover photos, content bodies, SEO titles, and tags.

### 🛰️ Central API Reference

All routes are prefixed under `/api/v1`.

#### 🛡️ Authentication & User Operations

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| POST | `/user/register` | Public | Registers a new account and sends email verification OTP. |
| POST | `/user/verify-otp` | Public | Verifies OTP code to activate the registered user account. |
| POST | `/user/resend-otp` | Public | Resends account activation code email. |
| POST | `/user/forgot-password` | Public | Requests a password reset verification code email. |
| POST | `/user/verify-forgot-otp` | Public | Validates a password reset OTP. |
| POST | `/user/resend-forgot-password-otp` | Public | Resends forgot password OTP. |
| GET | `/user/me` | Authenticated | Gets profile details of the logged-in user. |
| PATCH | `/user/update-profile` | Authenticated | Updates profile details (supports direct avatar file upload). |
| POST | `/auth/login` | Public | Authenticates and returns a secure JWT payload. |
| POST | `/auth/logout` | Public | Logs out user and destroys sessions. |

#### 🎨 Banner & Template Design APIs

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| POST | `/banner/generate` | Public | Generates 4 custom banner variants via AI prompting. |
| GET | `/banner/my-banner` | Authenticated | Fetches banners created by the logged-in user. |
| GET | `/banner/all-banners` | Public | Lists all public banners (supports paginated requests). |
| GET | `/banner/templates` | Public | Returns a list of all official pre-designed banner templates. |
| GET | `/banner/:id` | Public | Fetches a single banner/variant design. |
| POST | `/banner/create-banner-by-template` | Public | Configures and creates a banner mapping to an official template. |
| POST | `/banner/create-banner-from-template` | Authenticated | Generates a user banner copy from a template. |
| PATCH | `/banner/update-banner/:id` | Public | Updates banner attributes or modifies files. |

#### 📦 Order & Checkout Flow

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| POST | `/order/create-order` | Authenticated | Creates a new order linking a custom banner and sizes. |
| POST | `/order/checkout` | Authenticated | Validates shipping details and returns a Mollie checkout session URL. |
| GET | `/order/my-orders` | Authenticated | Returns logged-in user's order history with status checks. |
| GET | `/order/my-designs` | Authenticated | Returns orders designed by the current user. |
| GET | `/order/:id` | Authenticated | Fetches details of a specific order. |
| PATCH | `/order/cancel/:id` | Authenticated | Cancels a pending or processing order (sends confirmation email). |

#### 💳 Webhook & Payments Gateways

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| POST | `/payment/create-payment` | Authenticated | Begins standard payment transaction session. |
| POST | `/payment/mollie/webhook` | Public | Mollie payment status webhooks (Processes paid/failed events). |
| POST | `/stripe/webhook` | Public | Handles Stripe hooks (raw body parse). |

#### 📝 Blogs Catalog

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| GET | `/blog/` | Public | Lists published blog posts (supports category and keyword searches). |
| GET | `/blog/categories-tags` | Public | Returns unique tags and categories active in blogs. |
| GET | `/blog/id/:id` | Public | Fetches a single article post by its ID. |
| GET | `/blog/:slug` | Public | Fetches a single article by its SEO slug string. |

#### 🎈 Decoration Catalogs

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| GET | `/decorations/` | Public | Returns lists of party decoration catalog listings. |

#### ⚡ Unified Aggregation Endpoint

| Method | Endpoint | Authorization | Description |
|--------|----------|---------------|-------------|
| GET | `/aggregate/` | Public / Optional Auth | Returns all public lists (templates, banners, blogs, blog tags/categories, decorations, decoration categories, FAQs) in parallel. If a JWT is provided, it dynamically adds the logged-in user's profile, custom banners, and order history. |

#### 🛠️ Administrative Interfaces (Admin Role Only)

All administration endpoints are grouped under `/admin`.

- `GET /admin/total-orders` - Returns all orders in the system (paginated, with search filters).
- `PATCH /admin/update-order/:id` - Progresses order states (processing, ready, shipped, delivered, refunded, cancelled) and sends transaction updates.
- `GET /admin/total-users` - Returns registered users.
- `PATCH /admin/update-user/:id` - Updates user status flags (active, inactive, blocked).
- `GET /admin/dashboard-stats` - High-level metrics (total revenue, active user counts, pending queue count, deliveries).
- `GET /admin/total-transaction` - Complete transaction payment records.
- `GET /admin/decorations` - Admin list of decorations.
- `POST /admin/create-decoration` - Creates a party decoration card (supports multer upload).
- `POST /admin/create-decoration-category` - Adds a classification grouping name.
- `GET /admin/faqs` - Returns all FAQs.
- `POST /admin/create-faq` - Adds public FAQs.
- `POST /admin/create-template` - Uploads a standard banner design template.

### 📈 Background Tasks (BullMQ & Redis)

Decoupled queues process asynchronous workloads through Redis workers to maximize Express throughput:

- `mailQueue`: Processes email rendering and delivery templates asynchronously (OTPs, Order confirmations, Refund announcements).
- `aiChatQueue`: Manages AI conversational context.
- `cleanQueues`: Periodically flushes expired jobs in Redis storage to free RAM.

### 🛠️ Installation & Setup

#### Prerequisites

- Node.js (v18+)
- MongoDB Atlas connection string
- Redis server instance

#### Local Installation

```bash
npm install
```

Set up environment configurations by creating a `.env` file in the root matching the layout described below.

#### Synthesize Prisma database client types

```bash
npx prisma generate
```

#### Launch local development servers

```bash
npm run dev
```

### 🔒 Configuration Layout (.env)

```env
PORT=5000
NODE_ENV=development

DATABASE_URL="mongodb+srv://<username>:<password>@cluster.mongodb.net/basione_db"

JWT_SECRET="JWT_SECRET_SIGNING_KEY"
JWT_EXPIRES_IN="7d"
PASSWORD_SALT=10

SMTP_USER="smtp-client@basione.com"
SMTP_PASS="secure_smtp_password"

STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

MOLLIE_API_KEY="test_..."

CLOUDINARY_CLOUD_NAME="cloud-name"
CLOUDINARY_API_KEY="api-key"
CLOUDINARY_API_SECRET="api-secret"

S3_REGION="eu-central-1"
S3_ENDPOINT="https://s3.eu-central-1.amazonaws.com"
S3_BUCKET_NAME="basione-storage"
S3_ACCESS_KEY_ID="AWS_KEY_ID"
S3_SECRET_ACCESS_KEY="AWS_SECRET_KEY"

BASE_URL="http://localhost:5000"
CLIENT_URL="http://localhost:3000"
```

### 🏁 Building & Deployment

#### Production Compilation

Transpile TypeScript source trees to optimized ES modules:

```bash
npm run build
```

Launch the node server bundle:

```bash
node dist/server.js
```

#### Vercel Deployment

```bash
npm install -g vercel
vercel --prod
```

---

## Notes

This README is intended as a full product reference for the Basione platform. The current repository code may differ from the planned Node.js/Express server and Next.js client architecture described here.
