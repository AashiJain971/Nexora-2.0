# Nexora - MSME Business Platform

## Overview

Nexora is a comprehensive MSME (Micro, Small, and Medium Enterprises) business platform built with React and TypeScript. The application provides MSMEs with financial services, marketplace functionality, educational resources, and business tools. It features blockchain integration for wallet connectivity, invoice processing, loan discovery, and secure escrow services. The platform serves as a one-stop solution for MSME businesses to access loans, manage finances, sell products, and learn business skills.

## Recent Changes - January 2025

- **Rebranded to Nexora**: Updated platform name from "MSME Booster" to "Nexora" with lightning bolt logo
- **Enhanced UX**: Fixed text visibility issues on animated backgrounds with high-contrast styling
- **Floating AI Assistant**: Implemented persistent AI chatbot accessible from all pages
- **Functional Authentication**: Added complete frontend login system with demo credentials
- **Real Learning Content**: Integrated YouTube videos for business education modules
- **Design Improvements**: Enhanced color scheme and animations for professional appearance

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript and Vite for fast development and building
- **Routing**: Wouter for lightweight client-side routing
- **State Management**: TanStack Query (React Query) for server state management
- **UI Framework**: Radix UI components with shadcn/ui design system
- **Styling**: Tailwind CSS with custom CSS variables for theming
- **Form Handling**: React Hook Form with Zod validation

### Backend Architecture
- **Runtime**: Node.js with Express.js server
- **Language**: TypeScript with ES modules
- **Development**: Hot reload with Vite middleware integration
- **Storage Interface**: Abstract storage layer with in-memory implementation (MemStorage)
- **API Structure**: RESTful endpoints under `/api` prefix

### Database Design
- **ORM**: Drizzle ORM with PostgreSQL support
- **Schema**: Comprehensive business data model including:
  - Users and authentication
  - MSME business profiles with verification
  - Loan management with blockchain integration
  - Product catalog and marketplace
  - Reviews and ratings system
  - Business learning progress tracking

### Component Architecture
- **Modal System**: Centralized modal management for features like signup, invoice upload, loan discovery
- **Feature Components**: Modular components for business tools, marketplace, learning platform
- **UI Components**: Reusable design system components with consistent theming
- **Layout System**: Responsive navigation and layout components

### Key Features Implementation
- **Blockchain Integration**: Wallet connectivity simulation and smart contract addresses
- **AI Chatbot**: Business assistant with contextual responses
- **Invoice Processing**: File upload with AI-powered analysis
- **Learning Platform**: Video courses with progress tracking
- **Marketplace**: Product listing and buyer inquiry system
- **Business Analytics**: Dashboard with financial metrics and insights

## External Dependencies

### Core Framework Dependencies
- **React Ecosystem**: React 18, React DOM, React Hook Form, TanStack Query
- **UI Components**: Radix UI primitives for accessible components
- **Styling**: Tailwind CSS, class-variance-authority for component variants
- **Icons**: Lucide React for consistent iconography

### Development Tools
- **Build Tools**: Vite with TypeScript support and React plugin
- **Database**: Drizzle ORM with PostgreSQL dialect (@neondatabase/serverless)
- **Validation**: Zod for schema validation and type safety
- **Development**: tsx for TypeScript execution, esbuild for production builds

### Backend Dependencies
- **Server**: Express.js with TypeScript support
- **Database Connection**: Neon serverless PostgreSQL
- **Session Management**: connect-pg-simple for PostgreSQL session store
- **Development**: Replit-specific plugins for development environment

### Optional Integrations
- **Database**: PostgreSQL (configured but can be provisioned later)
- **Blockchain**: Wallet connection simulation (ready for Web3 integration)
- **File Processing**: Prepared for document/invoice processing services
- **Payment**: Structure ready for payment gateway integration