import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { AnimatedBackground } from '@/components/ui/animated-background';
import { FloatingParticles } from '@/components/ui/floating-particles';
import { SignupModal } from '@/components/features/signup-modal';
import { InvoiceUploadModal } from '@/components/features/invoice-upload-modal';
import { LoanDiscoveryModal } from '@/components/features/loan-discovery-modal';
import { EscrowModal } from '@/components/features/escrow-modal';
import { MarketplaceModal } from '@/components/features/marketplace-modal';
import { BusinessToolsModal } from '@/components/features/business-tools-modal';
import { LearningModal } from '@/components/features/learning-modal';
import { 
  Users, 
  File, 
  BadgeDollarSign, 
  Shield, 
  Store, 
  ChartLine,
  GraduationCap,
  ArrowRight,
  CheckCircle,
  XCircle,
  TrendingUp,
  Clock,
  Percent,
  Brain
} from 'lucide-react';

export default function Landing() {
  const [activeModal, setActiveModal] = useState<string | null>(null);

  const openModal = (modalName: string) => setActiveModal(modalName);
  const closeModal = () => setActiveModal(null);

  const scrollToFeatures = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToSolutions = () => {
    document.getElementById('solutions')?.scrollIntoView({ behavior: 'smooth' });
  };

  const features = [
    {
      id: 'signup',
      title: 'Quick MSME Sign-Up',
      description: 'Register your business and connect your wallet in minutes',
      icon: Users,
      color: 'teal',
      image: 'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
    {
      id: 'invoice',
      title: 'Invoice Management',
      description: 'Upload and manage invoices for instant loan eligibility',
      icon: File,
      color: 'orange',
      image: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
    {
      id: 'loans',
      title: 'Smart Loan Discovery',
      description: 'AI-powered matching with the best loan options',
      icon: BadgeDollarSign,
      color: 'green',
      image: 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
    {
      id: 'escrow',
      title: 'Blockchain Escrow',
      description: 'Secure milestone-based payments with smart contracts',
      icon: Shield,
      color: 'teal',
      image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
    {
      id: 'marketplace',
      title: 'Product Marketplace',
      description: 'List products and connect with verified buyers',
      icon: Store,
      color: 'orange',
      image: 'https://images.unsplash.com/photo-1515187029135-18ee286d815b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
    {
      id: 'tools',
      title: 'Business Tools',
      description: 'CRM, ERP, and analytics tools for growth',
      icon: ChartLine,
      color: 'green',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
    {
      id: 'learning',
      title: 'Learning Platform',
      description: 'Business courses and AI-powered guidance',
      icon: GraduationCap,
      color: 'teal',
      image: 'https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&h=200',
    },
  ];

  const problems = [
    {
      problem: 'No credit score = No loans',
      solution: 'Invoice-based creditworthiness assessment',
    },
    {
      problem: 'Complex loan processes',
      solution: 'AI-powered smart loan matching',
    },
    {
      problem: 'Limited market access',
      solution: 'Blockchain-verified buyer marketplace',
    },
    {
      problem: 'Trust issues in payments',
      solution: 'Smart contract escrow system',
    },
    {
      problem: 'Lack of business knowledge',
      solution: 'AI chatbot + video learning platform',
    },
  ];

  return (
    <div className="pt-16">
      {/* Landing Page with Animated Background */}
      <section id="home" className="relative min-h-screen animated-bg flex items-center justify-center overflow-hidden">
        <FloatingParticles />
        
        <div className="container mx-auto px-6 text-center relative z-10">
          <div className="animate-slide-up">
            <h2 className="text-4xl md:text-6xl font-bold mb-6 leading-tight text-high-contrast">
              Empowering <span className="text-orange-accent">MSMEs</span><br />
              with Blockchain & AI
            </h2>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto text-high-contrast">
              Loans, market access, tools, and trust — all in one platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Button
                onClick={() => openModal('signup')}
                className="bg-gradient-to-r from-orange-accent to-teal-accent px-8 py-4 text-lg font-semibold hover:scale-105 transform transition-all animate-glow"
              >
                Get Started <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button
                onClick={scrollToFeatures}
                variant="outline"
                className="border-teal-accent text-teal-accent hover:bg-teal-accent hover:text-background px-8 py-4 text-lg font-semibold"
              >
                Explore Features
              </Button>
            </div>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-fade-in">
            <Card className="glassmorphism p-6">
              <div className="text-3xl font-bold text-teal-accent">50K+</div>
              <div className="text-muted-foreground">MSMEs Registered</div>
            </Card>
            <Card className="glassmorphism p-6">
              <div className="text-3xl font-bold text-orange-accent">₹1.2B+</div>
              <div className="text-muted-foreground">Loans Processed</div>
            </Card>
            <Card className="glassmorphism p-6">
              <div className="text-3xl font-bold text-green-accent">95%</div>
              <div className="text-muted-foreground">Success Rate</div>
            </Card>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-background">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Complete MSME Ecosystem</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              From loan discovery to business tools, everything you need to grow your business
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div
                  key={feature.id}
                  className="block w-full h-full cursor-pointer"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`Feature clicked: ${feature.id} on ${window.innerWidth}px screen`);
                    openModal(feature.id);
                  }}
                  onTouchEnd={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`Feature touched: ${feature.id} on mobile`);
                    openModal(feature.id);
                  }}
                >
                  <Card className="h-full p-6 hover:border-teal-accent/50 transition-all duration-300 group hover:shadow-lg hover:shadow-teal-accent/20 active:scale-95">
                    <img 
                      src={feature.image} 
                      alt={feature.title}
                      className="w-full h-32 object-cover rounded-lg mb-4 pointer-events-none"
                    />
                    <Icon className={`w-8 h-8 text-${feature.color}-accent mb-4 pointer-events-none`} />
                    <h3 className="text-xl font-semibold mb-2 pointer-events-none">{feature.title}</h3>
                    <p className="text-muted-foreground mb-4 pointer-events-none">{feature.description}</p>
                    <div className="text-teal-accent text-sm font-medium group-hover:text-green-accent transition-colors pointer-events-none">
                      Click to explore →
                    </div>
                  </Card>
                </div>
              );
            })}
          </div>


        </div>
      </section>

      {/* Problem vs Solution Section */}
      <section id="solutions" className="py-20 bg-muted/20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Solving Real MSME Challenges</h2>
            <p className="text-muted-foreground text-lg">Traditional problems, blockchain solutions</p>
          </div>

          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-teal-accent to-green-accent">
                  <tr>
                    <th className="px-6 py-4 text-left font-semibold text-background">Traditional Problems</th>
                    <th className="px-6 py-4 text-left font-semibold text-background">MSME Booster Solutions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {problems.map((item, index) => (
                    <tr key={index} className="hover:bg-muted/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <XCircle className="w-5 h-5 text-red-400" />
                          <span>{item.problem}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-3">
                          <CheckCircle className="w-5 h-5 text-green-accent" />
                          <span>{item.solution}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </section>

      {/* Impact Section */}
      <section className="py-20 bg-gradient-to-r from-muted/50 to-background">
        <div className="container mx-auto px-6 text-center">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-5xl font-bold mb-6">
              Helping MSMEs grow faster,<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-accent to-green-accent">
                even without a credit score!
              </span>
            </h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of MSMEs who are already transforming their businesses with blockchain technology and AI-powered insights.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button 
                onClick={() => openModal('signup')}
                className="bg-gradient-to-r from-teal-accent to-green-accent px-8 py-4 text-lg font-semibold hover:scale-105 transform transition-all"
              >
                Start Your Journey
              </Button>
              <Button 
                onClick={scrollToFeatures}
                variant="outline"
                className="border-teal-accent text-teal-accent hover:bg-teal-accent hover:text-background px-8 py-4 text-lg font-semibold"
              >
                Explore Features
              </Button>
            </div>
            
            {/* Final Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <div className="text-4xl font-bold text-green-accent mb-2">Zero</div>
                <div className="text-muted-foreground">Credit Score Required</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-teal-accent mb-2">24/7</div>
                <div className="text-muted-foreground">AI Support Available</div>
              </div>
              <div>
                <div className="text-4xl font-bold text-orange-accent mb-2">100%</div>
                <div className="text-muted-foreground">Blockchain Secured</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted/20 py-12 border-t border-border">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-6 h-6 bg-teal-accent rounded-lg"></div>
                <span className="text-lg font-bold">Nexora</span>
              </div>
              <p className="text-muted-foreground text-sm">
                Empowering small businesses with blockchain technology and AI-driven insights.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-muted-foreground text-sm">
                <li><a href="#" className="hover:text-teal-accent transition-colors">Loan Discovery</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Marketplace</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Business Tools</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Learning Center</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-muted-foreground text-sm">
                <li><a href="#" className="hover:text-teal-accent transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">API Reference</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Contact Us</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-muted-foreground text-sm">
                <li><a href="#" className="hover:text-teal-accent transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Cookie Policy</a></li>
                <li><a href="#" className="hover:text-teal-accent transition-colors">Compliance</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-border pt-8 mt-8 text-center text-muted-foreground text-sm">
            <p>&copy; 2024 Nexora. All rights reserved. Built with ❤️ for small businesses.</p>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <SignupModal open={activeModal === 'signup'} onOpenChange={closeModal} />
      <InvoiceUploadModal open={activeModal === 'invoice'} onOpenChange={(open) => !open && closeModal()} />
      <LoanDiscoveryModal open={activeModal === 'loans'} onOpenChange={closeModal} />
      <EscrowModal open={activeModal === 'escrow'} onOpenChange={(open) => !open && closeModal()} />
      <MarketplaceModal open={activeModal === 'marketplace'} onOpenChange={closeModal} />
      <BusinessToolsModal open={activeModal === 'tools'} onOpenChange={closeModal} />
      <LearningModal open={activeModal === 'learning'} onOpenChange={closeModal} />
      

    </div>
  );
}
