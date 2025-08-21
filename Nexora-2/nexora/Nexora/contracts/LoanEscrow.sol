// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoanEscrow {
    address public admin;
    uint256 public totalEscrowBalance;
    
    struct LoanRequest {
        address borrower;
        uint256 amount;
        uint256 creditScore;
        bool approved;
        bool disbursed;
        bool repaid;
        uint256 timestamp;
        string businessName;
        string businessType;
    }
    
    struct Lender {
        address lenderAddress;
        uint256 depositedAmount;
        bool isActive;
        string name;
    }
    
    mapping(address => LoanRequest[]) public borrowerLoans;
    mapping(address => Lender) public lenders;
    mapping(uint256 => LoanRequest) public loanRequests;
    address[] public lenderAddresses;
    
    uint256 public nextLoanId;
    uint256 public constant MINIMUM_CREDIT_SCORE = 600;
    uint256 public constant MAXIMUM_LOAN_PERCENTAGE = 80; // 80% of escrow can be loaned
    
    event FundsDeposited(address indexed lender, uint256 amount, string name);
    event LoanRequested(address indexed borrower, uint256 loanId, uint256 amount, uint256 creditScore);
    event LoanApproved(uint256 indexed loanId, address indexed borrower, uint256 amount);
    event LoanDisbursed(uint256 indexed loanId, address indexed borrower, uint256 amount);
    event LoanRepaid(uint256 indexed loanId, address indexed borrower, uint256 amount);
    event FundsWithdrawn(address indexed lender, uint256 amount);
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    modifier onlyLender() {
        require(lenders[msg.sender].isActive, "Only active lenders can perform this action");
        _;
    }
    
    constructor() {
        admin = msg.sender;
        nextLoanId = 1;
    }
    
    // Lenders deposit funds to the escrow
    function depositFunds(string memory _lenderName) external payable {
        require(msg.value > 0, "Must deposit more than 0 ETH");
        
        if (!lenders[msg.sender].isActive) {
            lenders[msg.sender] = Lender({
                lenderAddress: msg.sender,
                depositedAmount: msg.value,
                isActive: true,
                name: _lenderName
            });
            lenderAddresses.push(msg.sender);
        } else {
            lenders[msg.sender].depositedAmount += msg.value;
        }
        
        totalEscrowBalance += msg.value;
        emit FundsDeposited(msg.sender, msg.value, _lenderName);
    }
    
    // Borrowers request loans
    function requestLoan(
        uint256 _amount, 
        uint256 _creditScore,
        string memory _businessName,
        string memory _businessType
    ) external {
        require(_amount > 0, "Loan amount must be greater than 0");
        require(_creditScore >= MINIMUM_CREDIT_SCORE, "Credit score too low");
        require(_amount <= (totalEscrowBalance * MAXIMUM_LOAN_PERCENTAGE) / 100, "Requested amount exceeds available funds");
        
        LoanRequest memory newLoan = LoanRequest({
            borrower: msg.sender,
            amount: _amount,
            creditScore: _creditScore,
            approved: false,
            disbursed: false,
            repaid: false,
            timestamp: block.timestamp,
            businessName: _businessName,
            businessType: _businessType
        });
        
        borrowerLoans[msg.sender].push(newLoan);
        loanRequests[nextLoanId] = newLoan;
        
        emit LoanRequested(msg.sender, nextLoanId, _amount, _creditScore);
        nextLoanId++;
    }
    
    // Admin approves loans based on credit score
    function approveLoan(uint256 _loanId) external onlyAdmin {
        require(_loanId < nextLoanId, "Invalid loan ID");
        require(!loanRequests[_loanId].approved, "Loan already approved");
        require(!loanRequests[_loanId].disbursed, "Loan already disbursed");
        require(loanRequests[_loanId].amount <= totalEscrowBalance, "Insufficient escrow balance");
        
        loanRequests[_loanId].approved = true;
        emit LoanApproved(_loanId, loanRequests[_loanId].borrower, loanRequests[_loanId].amount);
    }
    
    // Disburse approved loans
    function disburseLoan(uint256 _loanId) external onlyAdmin {
        require(_loanId < nextLoanId, "Invalid loan ID");
        require(loanRequests[_loanId].approved, "Loan not approved");
        require(!loanRequests[_loanId].disbursed, "Loan already disbursed");
        require(loanRequests[_loanId].amount <= totalEscrowBalance, "Insufficient escrow balance");
        
        loanRequests[_loanId].disbursed = true;
        totalEscrowBalance -= loanRequests[_loanId].amount;
        
        payable(loanRequests[_loanId].borrower).transfer(loanRequests[_loanId].amount);
        
        emit LoanDisbursed(_loanId, loanRequests[_loanId].borrower, loanRequests[_loanId].amount);
    }
    
    // Borrowers repay loans
    function repayLoan(uint256 _loanId) external payable {
        require(_loanId < nextLoanId, "Invalid loan ID");
        require(loanRequests[_loanId].borrower == msg.sender, "Only borrower can repay");
        require(loanRequests[_loanId].disbursed, "Loan not disbursed");
        require(!loanRequests[_loanId].repaid, "Loan already repaid");
        require(msg.value >= loanRequests[_loanId].amount, "Insufficient repayment amount");
        
        loanRequests[_loanId].repaid = true;
        totalEscrowBalance += msg.value;
        
        emit LoanRepaid(_loanId, msg.sender, msg.value);
    }
    
    // Lenders can withdraw their proportional share
    function withdrawFunds(uint256 _amount) external onlyLender {
        require(_amount > 0, "Amount must be greater than 0");
        require(lenders[msg.sender].depositedAmount >= _amount, "Insufficient deposited amount");
        require(totalEscrowBalance >= _amount, "Insufficient escrow balance");
        
        lenders[msg.sender].depositedAmount -= _amount;
        totalEscrowBalance -= _amount;
        
        if (lenders[msg.sender].depositedAmount == 0) {
            lenders[msg.sender].isActive = false;
        }
        
        payable(msg.sender).transfer(_amount);
        emit FundsWithdrawn(msg.sender, _amount);
    }
    
    // View functions
    function getEscrowBalance() external view returns (uint256) {
        return totalEscrowBalance;
    }
    
    function getLoanRequest(uint256 _loanId) external view returns (LoanRequest memory) {
        return loanRequests[_loanId];
    }
    
    function getBorrowerLoans(address _borrower) external view returns (LoanRequest[] memory) {
        return borrowerLoans[_borrower];
    }
    
    function getLender(address _lenderAddress) external view returns (Lender memory) {
        return lenders[_lenderAddress];
    }
    
    function getAllLenders() external view returns (address[] memory) {
        return lenderAddresses;
    }
    
    function calculateMaxLoanAmount(uint256 _creditScore) external view returns (uint256) {
        if (_creditScore < MINIMUM_CREDIT_SCORE) {
            return 0;
        }
        
        uint256 maxAmount = (totalEscrowBalance * MAXIMUM_LOAN_PERCENTAGE) / 100;
        
        // Adjust based on credit score
        if (_creditScore >= 800) {
            return maxAmount;
        } else if (_creditScore >= 700) {
            return (maxAmount * 80) / 100;
        } else if (_creditScore >= 650) {
            return (maxAmount * 60) / 100;
        } else {
            return (maxAmount * 40) / 100;
        }
    }
}
