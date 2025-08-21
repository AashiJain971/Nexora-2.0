# Blockchain Loan System - Nexora

A decentralized lending platform that uses credit scores calculated from uploaded invoices to determine loan eligibility and amounts. The system uses smart contracts for escrow management and transparent loan processing.

## 🌟 Features

### For Borrowers

- **Credit Score-Based Loans**: Get loans based on your calculated credit score from business invoices
- **Instant Evaluation**: Real-time credit score calculation and loan amount estimation
- **Transparent Process**: All loan requests and approvals recorded on blockchain
- **Flexible Amounts**: Borrow up to your credit score limit from the escrow pool

### For Lenders

- **Secure Escrow**: Deposit funds to a smart contract-managed escrow
- **Earn Returns**: Get returns when borrowers repay loans with interest
- **Risk Management**: Credit score-based loan approval reduces default risk
- **Transparent Tracking**: Monitor all deposits and loan activities on-chain

### For Administrators

- **Loan Management**: Approve/reject loan requests based on credit scores
- **Escrow Oversight**: Monitor total escrow balance and utilization
- **Transaction History**: Track all blockchain transactions and events
- **Risk Controls**: Set minimum credit scores and maximum loan percentages

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Blockchain    │
│   (React)       │    │   (FastAPI)     │    │   (Ethereum)    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Wallet UI     │◄──►│ • Credit Score  │◄──►│ • LoanEscrow    │
│ • Loan Forms    │    │ • User Auth     │    │   Contract      │
│ • Dashboard     │    │ • Invoice AI    │    │ • Events        │
│ • Admin Panel   │    │ • Database      │    │ • Transactions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- MetaMask wallet
- Testnet ETH (Sepolia)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nexora-blockchain-loans
```

### 2. Setup Backend

```bash
cd python_services
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

### 3. Setup Frontend

```bash
cd client
npm install

# Update contract address in src/lib/blockchain.ts
```

### 4. Deploy Smart Contract

Follow the [Deployment Guide](./DEPLOYMENT_GUIDE.md) to deploy the LoanEscrow contract.

### 5. Start Services

```bash
# Terminal 1: Backend
cd python_services
python combined_api.py

# Terminal 2: Frontend
cd client
npm run dev
```

## 💡 How It Works

### 1. Credit Score Calculation

1. User uploads business invoices
2. AI extracts invoice data (amounts, dates, clients)
3. Credit score calculated based on:
   - Number of invoices
   - Total transaction volume
   - Payment completion rate
   - Business consistency

### 2. Loan Request Process

1. User connects Web3 wallet
2. System fetches current credit score
3. User fills loan request form with:
   - Loan amount (within credit limit)
   - Business name and type
   - Wallet address
4. Transaction submitted to blockchain

### 3. Loan Approval (Admin)

1. Admin reviews loan requests
2. Checks credit score meets minimum (600+)
3. Verifies escrow has sufficient funds
4. Approves loan on blockchain

### 4. Loan Disbursement

1. Approved loans can be disbursed
2. ETH transferred from escrow to borrower
3. Loan marked as active
4. Repayment tracking begins

### 5. Repayment

1. Borrower repays loan + interest
2. Funds returned to escrow
3. Available for new loans
4. Lenders earn proportional returns

## 📊 Credit Score Algorithm

The system calculates credit scores based on:

```python
# Factors (weighted):
- Invoice Volume (30%): Total transaction amounts
- Payment History (25%): Completed vs pending payments
- Business Stability (20%): Consistency of invoice amounts
- Transaction Frequency (15%): Number of invoices over time
- Client Diversity (10%): Number of different clients

# Score Ranges:
800-850: Excellent (90% of max loan)
750-799: Very Good (80% of max loan)
700-749: Good (70% of max loan)
650-699: Fair (60% of max loan)
600-649: Poor (50% of max loan)
<600: Not eligible
```

## 🔐 Smart Contract Security

### LoanEscrow Contract Features

- **Admin Controls**: Only admin can approve/disburse loans
- **Credit Score Validation**: Minimum score requirements enforced
- **Escrow Limits**: Maximum 80% of escrow can be loaned out
- **Event Logging**: All actions recorded as blockchain events
- **Emergency Controls**: Admin can pause contract if needed

### Security Measures

- Reentrancy protection
- Overflow/underflow protection
- Access control modifiers
- Input validation
- Gas optimization

## 🎯 User Interface

### Borrower Dashboard

- Current credit score display
- Maximum loan amount calculator
- Loan request form
- Active loans status
- Repayment interface

### Lender Interface

- Escrow deposit form
- Current balance display
- Return calculations
- Withdrawal options
- Portfolio overview

### Admin Panel

- Pending loan requests
- Approval/rejection tools
- Escrow monitoring
- System statistics
- User management

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# AI Services
GROQ_API_KEY=your_groq_api_key

# Blockchain
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
LOAN_ESCROW_ADDRESS=0xYourContractAddress
ADMIN_PRIVATE_KEY=0xYourAdminPrivateKey

# Security
JWT_SECRET_KEY=your_jwt_secret_key
```

#### Frontend (blockchain.ts)

```typescript
export const LOAN_ESCROW_ADDRESS = "0xYourContractAddress";
```

## 📊 Database Schema

### Key Tables

- `users`: User authentication and profiles
- `invoices`: Uploaded invoice data for credit scoring
- `blockchain_loans`: Loan requests and status tracking
- `lender_deposits`: Escrow deposit history
- `loan_events`: Blockchain event logging

## 🧪 Testing

### Unit Tests

```bash
# Backend tests
cd python_services
pytest tests/

# Frontend tests
cd client
npm test
```

### Integration Tests

```bash
# Test full loan flow
npm run test:integration

# Test smart contract
npx hardhat test
```

### Manual Testing Checklist

- [ ] Upload invoice and verify credit score
- [ ] Request loan with valid credit score
- [ ] Admin approve loan request
- [ ] Disburse approved loan
- [ ] Lender deposit funds
- [ ] Borrower repay loan
- [ ] Verify all blockchain events

## 🚨 Risk Warnings

⚠️ **Important Disclaimers:**

1. **Experimental Software**: This is a proof-of-concept DeFi application
2. **Smart Contract Risk**: Bugs could result in loss of funds
3. **Market Risk**: Cryptocurrency values are volatile
4. **Regulatory Risk**: DeFi regulations are evolving
5. **Credit Risk**: Borrowers may default on loans

**Only use testnet and test funds. Never invest more than you can afford to lose.**

## 🛠️ Development

### Project Structure

```
nexora-blockchain-loans/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── hooks/         # React hooks
│   │   ├── lib/           # Utilities
│   │   └── pages/         # Route components
├── python_services/       # FastAPI backend
│   ├── combined_api.py    # Main API
│   ├── blockchain_loan_api.py # Blockchain integration
│   ├── credit_score.py    # Credit scoring logic
│   └── invoice_2.py       # Invoice processing
├── contracts/             # Smart contracts
│   └── LoanEscrow.sol     # Main escrow contract
└── docs/                  # Documentation
```

### Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Submit pull request

### API Documentation

- Backend API: `http://localhost:8001/docs`
- Endpoints documented with OpenAPI/Swagger

## 📈 Roadmap

### Phase 1 (Current)

- [x] Basic credit scoring from invoices
- [x] Smart contract escrow system
- [x] Web3 wallet integration
- [x] Loan request/approval flow

### Phase 2 (Planned)

- [ ] Interest rate calculations
- [ ] Automated loan approvals
- [ ] Advanced credit scoring models
- [ ] Mobile app support

### Phase 3 (Future)

- [ ] Cross-chain support
- [ ] Institutional lender integration
- [ ] Insurance products
- [ ] Governance token

## 📞 Support

### Getting Help

- Check [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- Review error logs in browser console
- Test on Sepolia testnet first
- Join our Discord community

### Common Issues

1. **MetaMask Connection**: Ensure you're on the correct network
2. **Transaction Failures**: Check gas fees and wallet balance
3. **Credit Score Issues**: Verify invoice upload completed
4. **Contract Errors**: Confirm contract address is correct

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the future of decentralized finance**
