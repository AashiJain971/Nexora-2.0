// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract LoanEscrow {
    struct Loan {
        address borrower;
        address lender;
        uint256 amount;
        uint256 interestRate;
        uint256 duration;
        uint256 createdAt;
        uint256 dueDate;
        bool funded;
        bool repaid;
        bool defaulted;
    }

    mapping(uint256 => Loan) public loans;
    uint256 public nextLoanId;

    event LoanCreated(uint256 indexed loanId, address indexed borrower, uint256 amount);
    event LoanFunded(uint256 indexed loanId, address indexed lender);
    event LoanRepaid(uint256 indexed loanId);
    event LoanDefaulted(uint256 indexed loanId);

    function createLoan(uint256 _amount, uint256 _interestRate, uint256 _duration) external returns (uint256) {
        uint256 loanId = nextLoanId++;
        
        loans[loanId] = Loan({
            borrower: msg.sender,
            lender: address(0),
            amount: _amount,
            interestRate: _interestRate,
            duration: _duration,
            createdAt: block.timestamp,
            dueDate: 0,
            funded: false,
            repaid: false,
            defaulted: false
        });

        emit LoanCreated(loanId, msg.sender, _amount);
        return loanId;
    }

    function fundLoan(uint256 _loanId) external payable {
        Loan storage loan = loans[_loanId];
        require(loan.borrower != address(0), "Loan does not exist");
        require(!loan.funded, "Loan already funded");
        require(msg.value == loan.amount, "Incorrect funding amount");

        loan.lender = msg.sender;
        loan.funded = true;
        loan.dueDate = block.timestamp + loan.duration;

        payable(loan.borrower).transfer(msg.value);
        emit LoanFunded(_loanId, msg.sender);
    }

    function repayLoan(uint256 _loanId) external payable {
        Loan storage loan = loans[_loanId];
        require(loan.funded, "Loan not funded");
        require(!loan.repaid && !loan.defaulted, "Loan already settled");
        require(msg.sender == loan.borrower, "Only borrower can repay");

        uint256 repaymentAmount = loan.amount + (loan.amount * loan.interestRate / 100);
        require(msg.value == repaymentAmount, "Incorrect repayment amount");

        loan.repaid = true;
        payable(loan.lender).transfer(msg.value);
        emit LoanRepaid(_loanId);
    }

    function markDefault(uint256 _loanId) external {
        Loan storage loan = loans[_loanId];
        require(loan.funded, "Loan not funded");
        require(!loan.repaid && !loan.defaulted, "Loan already settled");
        require(block.timestamp > loan.dueDate, "Loan not yet due");

        loan.defaulted = true;
        emit LoanDefaulted(_loanId);
    }

    function getLoan(uint256 _loanId) external view returns (Loan memory) {
        return loans[_loanId];
    }
}
