export const dummyBusinessProfile = {
  id: "1",
  businessName: "Artisan Crafts Co.",
  registrationNumber: "UDYAM-MH-03-0012345",
  businessType: "Manufacturing",
  category: "Traditional Handicrafts",
  establishedYear: 2019,
  location: "Mumbai, India",
  employees: 12,
  annualRevenue: "5000000",
  walletAddress: "0x1234567890abcdef",
  // creditScore removed - now fetched from API
  isVerified: true,
};

export const dummyLoans = [
  {
    id: "1",
    lenderName: "FinTech Capital",
    amount: "500000",
    interestRate: "6.5",
    tenure: 24,
    status: "active",
    disbursedAmount: "500000",
    repaidAmount: "125000",
    contractAddress: "0xabc123def456",
    rating: 4.9,
    reviews: 234,
    processingFee: "1.5",
    approvalTime: "24 hours",
    features: ["No Collateral", "Flexible Terms", "Early Repayment"],
  },
  {
    id: "2",
    lenderName: "SME Growth Fund",
    amount: "750000",
    interestRate: "8.2",
    tenure: 36,
    status: "processing",
    disbursedAmount: "0",
    repaidAmount: "0",
    contractAddress: null,
    rating: 4.7,
    reviews: 156,
    processingFee: "2.0",
    approvalTime: "48 hours",
    features: ["Government Backed", "Mentorship Program", "Grace Period"],
  },
  {
    id: "3",
    lenderName: "Green Business Loans",
    amount: "300000",
    interestRate: "4.9",
    tenure: 18,
    status: "available",
    disbursedAmount: "0",
    repaidAmount: "0",
    contractAddress: null,
    rating: 4.8,
    reviews: 89,
    processingFee: "1.0",
    approvalTime: "72 hours",
    features: ["Eco-Friendly", "Tax Benefits", "Carbon Credits"],
  },
];

export const dummyProducts = [
  {
    id: "1",
    name: "Handcrafted Wooden Table",
    description: "Premium quality teak wood dining table with traditional craftsmanship",
    category: "Furniture",
    price: "45000",
    minOrder: 1,
    stock: 15,
    imageUrl: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",
    views: 12,
    inquiries: 3,
  },
  {
    id: "2",
    name: "Handwoven Silk Scarf",
    description: "Traditional silk scarf with intricate patterns, made by local artisans",
    category: "Textiles",
    price: "8500",
    minOrder: 5,
    stock: 3,
    imageUrl: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
    views: 28,
    inquiries: 7,
  },
  {
    id: "3",
    name: "Organic Spice Collection",
    description: "Premium organic spices sourced directly from local farmers",
    category: "Food & Beverages",
    price: "3500",
    minOrder: 10,
    stock: 28,
    imageUrl: "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
    views: 45,
    inquiries: 12,
  },
  {
    id: "4",
    name: "Smart Home Sensor Kit",
    description: "IoT-enabled home automation sensors with mobile app control",
    category: "Electronics",
    price: "12500",
    minOrder: 1,
    stock: 12,
    imageUrl: "https://images.unsplash.com/photo-1498049794561-7780e7231661",
    views: 67,
    inquiries: 15,
  },
];

export const dummyInvoices = [
  {
    id: "1",
    invoiceNumber: "INV-2024-001",
    amount: "525000",
    clientName: "TechCorp Solutions",
    dueDate: "2024-03-15",
    status: "verified",
    isVerified: true,
    blockchainTxHash: "0x123abc456def",
  },
  {
    id: "2",
    invoiceNumber: "INV-2024-002",
    amount: "187500",
    clientName: "Retail Chain Ltd",
    dueDate: "2024-03-20",
    status: "pending",
    isVerified: false,
    blockchainTxHash: null,
  },
];

export const dummyBadges = [
  {
    id: "1",
    name: "Reliable Payer",
    description: "100% on-time payments",
    iconType: "crown",
    color: "gold",
    earnedAt: "2024-02-15",
  },
  {
    id: "2",
    name: "Growth Champion",
    description: "50% revenue increase",
    iconType: "chart-line",
    color: "blue",
    earnedAt: "2024-01-20",
  },
  {
    id: "3",
    name: "Eco Warrior",
    description: "Sustainable practices",
    iconType: "leaf",
    color: "green",
    earnedAt: "2023-12-10",
  },
  {
    id: "4",
    name: "Community Builder",
    description: "Helped 10+ MSMEs",
    iconType: "handshake",
    color: "purple",
    earnedAt: "2023-11-05",
  },
  {
    id: "5",
    name: "Innovation Leader",
    description: "Tech adoption pioneer",
    iconType: "rocket",
    color: "red",
    earnedAt: "2023-10-15",
  },
  {
    id: "6",
    name: "Learning Enthusiast",
    description: "Completed 15 courses",
    iconType: "graduation-cap",
    color: "orange",
    earnedAt: "2023-09-20",
  },
];

export const dummyOrders = [
  {
    id: "ORD-001",
    customer: "John Smith",
    product: "Wooden Table",
    amount: "45000",
    status: "delivered",
    date: "2024-02-20",
  },
  {
    id: "ORD-002",
    customer: "Sarah Wilson",  
    product: "Silk Scarf",
    amount: "8500",
    status: "processing",
    date: "2024-02-22",
  },
  {
    id: "ORD-003",
    customer: "TechCorp",
    product: "Sensor Kit (x10)",
    amount: "125000",
    status: "shipped",
    date: "2024-02-18",
  },
];

export const dummyCustomers = [
  {
    id: "1",
    name: "TechCorp Solutions",
    email: "contact@techcorp.com",
    orders: 5,
    totalSpent: "325000",
    avatar: "TC",
  },
  {
    id: "2",
    name: "Artisan Marketplace",
    email: "buyers@artisan.com",
    orders: 3,
    totalSpent: "189000",
    avatar: "AM",
  },
  {
    id: "3",
    name: "John Smith",
    email: "john@email.com",
    orders: 2,
    totalSpent: "53500",
    avatar: "JS",
  },
];

export const dummyExpenses = [
  {
    category: "Raw Materials",
    amount: "120000",
    color: "red",
  },
  {
    category: "Transportation",
    amount: "45000",
    color: "orange",
  },
  {
    category: "Utilities",
    amount: "25000",
    color: "teal",
  },
  {
    category: "Marketing",
    amount: "44567",
    color: "green",
  },
];

export const dummyRecentExpenses = [
  {
    name: "Wood Purchase",
    amount: "25000",
    date: "2 days ago",
  },
  {
    name: "Delivery Charges",
    amount: "3500",
    date: "3 days ago",
  },
  {
    name: "Electricity Bill",
    amount: "8200",
    date: "5 days ago",
  },
];

export const dummyLearningProgress = [
  {
    course: "Digital Marketing",
    progress: 85,
    color: "teal",
  },
  {
    course: "Financial Planning",
    progress: 45,
    color: "orange",
  },
  {
    course: "Supply Chain",
    progress: 20,
    color: "green",
  },
];

export const dummyLearningCourses = [
  {
    id: "1",
    title: "Digital Marketing for Small Businesses",
    description: "Learn how to leverage social media and online platforms to grow your customer base",
    duration: "25:30",
    difficulty: "Beginner",
    rating: 4.8,
    progress: 60,
    thumbnail: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43",
  },
  {
    id: "2",
    title: "Financial Planning Basics",
    description: "Master the fundamentals of business financial planning",
    duration: "15:00",
    difficulty: "Beginner",
    thumbnail: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
  },
  {
    id: "3",
    title: "Building Customer Relationships",
    description: "Strategies for maintaining long-term customer relationships",
    duration: "22:00",
    difficulty: "Intermediate",
    thumbnail: "https://images.unsplash.com/photo-1515187029135-18ee286d815b",
  },
  {
    id: "4",
    title: "Supply Chain Management",
    description: "Optimize your supply chain for better efficiency",
    duration: "18:00",
    difficulty: "Advanced",
    thumbnail: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d",
  },
];

export const dummyAIResponses = [
  "Based on your business profile, I recommend focusing on digital marketing to increase sales by 25-30%.",
  "Your credit score can be improved by maintaining consistent invoice payments and reducing outstanding debts.",
  "Consider applying for our equipment loan with 6.5% interest rate - it matches your business needs perfectly.",
  "I've analyzed your expenses and found potential savings of ₹15,000/month in transportation costs.",
  "Your business is eligible for our premium marketplace listing. This could increase inquiries by 40%.",
  "The current market trend shows 15% growth in your product category. Consider expanding inventory.",
  "Your payment history is excellent! You qualify for our lowest interest rate loans.",
  "I notice seasonal patterns in your sales. Consider diversifying your product line for stable revenue.",
];

export const dummyEscrowMilestones = [
  {
    id: 1,
    title: "Initial Documentation",
    description: "Submit all required business documents and KYC",
    amount: "70000",
    percentage: 20,
    status: "completed",
    completedDate: "2024-01-15",
  },
  {
    id: 2,
    title: "Business Setup",
    description: "Complete business registration and initial setup",
    amount: "105000",
    percentage: 30,
    status: "in-progress",
    completedDate: null,
  },
  {
    id: 3,
    title: "Inventory Purchase",
    description: "Purchase initial inventory and equipment",
    amount: "105000",
    percentage: 30,
    status: "pending",
    completedDate: null,
  },
  {
    id: 4,
    title: "Business Launch",
    description: "Launch business operations and first sales",
    amount: "70000",
    percentage: 20,
    status: "pending",
    completedDate: null,
  },
];

export const dummyMarketplaceProducts = [
  {
    id: "1",
    name: "Handcrafted Wooden Chairs",
    description: "Premium quality wooden chairs made from sustainable teak wood",
    price: "2500",
    minOrder: 50,
    category: "Furniture",
    seller: "Woodcraft Industries",
    image: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",
  },
  {
    id: "2",
    name: "Organic Spice Mix",
    description: "Authentic Indian spice blends made from organic ingredients",
    price: "150",
    minOrder: 100,
    category: "Food & Beverages",
    seller: "Spice Garden Co.",
    image: "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
  },
  {
    id: "3",
    name: "Handwoven Cotton Fabrics",
    description: "Traditional cotton fabrics with modern designs",
    price: "300",
    minOrder: 200,
    category: "Textiles",
    seller: "Textile Artisans",
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
  },
];

export const dummyBuyerInquiries = [
  {
    id: "1",
    buyerName: "TechCorp Solutions",
    productName: "Smart Home Sensor Kit",
    quantity: 50,
    message: "Interested in bulk purchase for our office setup",
    matchPercentage: 95,
    avatar: "TC",
  },
  {
    id: "2",
    buyerName: "Artisan Marketplace",
    productName: "Handwoven Silk Scarves",
    quantity: 25,
    message: "Looking for exclusive partnership for online sales",
    matchPercentage: 88,
    avatar: "AM",
  },
];
