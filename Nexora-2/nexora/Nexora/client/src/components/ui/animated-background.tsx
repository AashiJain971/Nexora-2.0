interface AnimatedBackgroundProps {
  children: React.ReactNode;
}

export function AnimatedBackground({ children }: AnimatedBackgroundProps) {
  return (
    <div className="relative min-h-screen animated-bg overflow-hidden">
      {/* Floating background elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="w-96 h-96 bg-teal-accent rounded-full mix-blend-multiply filter blur-xl animate-float absolute top-20 left-20"></div>
        <div className="w-96 h-96 bg-orange-accent rounded-full mix-blend-multiply filter blur-xl animate-float absolute top-40 right-20" style={{ animationDelay: '2s' }}></div>
        <div className="w-96 h-96 bg-green-accent rounded-full mix-blend-multiply filter blur-xl animate-float absolute bottom-20 left-1/2 transform -translate-x-1/2" style={{ animationDelay: '4s' }}></div>
      </div>
      
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
