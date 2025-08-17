import { useState } from 'react';
import { useLocation } from 'wouter';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { LogIn, Eye, EyeOff, Zap } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LoginModal({ open, onOpenChange }: LoginModalProps) {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<LoginFormData>({
    defaultValues: {
      email: '',
      password: '',
    },
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8001/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: data.email,
          password: data.password,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        // Store token and user info
        localStorage.setItem('nexora_token', result.token);
        localStorage.setItem('nexora_user', JSON.stringify({
          id: result.user.id,
          email: result.user.email,
          full_name: result.user.full_name,
          loginTime: new Date().toISOString(),
        }));
        
        toast({
          title: 'Login Successful',
          description: 'Welcome back to Nexora!',
        });
        
        onOpenChange(false);
        setLocation('/dashboard');
      } else {
        toast({
          title: 'Login Failed',
          description: result.detail || 'Invalid credentials',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Login error:', error);
      toast({
        title: 'Login Failed',
        description: 'Network error. Please try again.',
        variant: 'destructive',
      });
    }
    
    setIsLoading(false);
  };

  const handleDemoLogin = () => {
    form.setValue('email', 'demo@nexora.com');
    form.setValue('password', 'demo123');
    form.handleSubmit(onSubmit)();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-orange-accent to-teal-accent rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-background" />
            </div>
          </div>
          <DialogTitle className="text-2xl font-bold">Welcome to Nexora</DialogTitle>
          <p className="text-muted-foreground">
            Sign in to access your MSME dashboard
          </p>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email Address</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="Enter your email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        {...field}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          
            <div className="space-y-2">
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-teal-accent to-green-accent hover:opacity-90"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-background border-t-transparent rounded-full animate-spin mr-2" />
                    Signing In...
                  </>
                ) : (
                  <>
                    <LogIn className="w-4 h-4 mr-2" />
                    Sign In
                  </>
                )}
              </Button>

              <Button 
                type="button"
                variant="outline"
                className="w-full"
                onClick={handleDemoLogin}
                disabled={isLoading}
              >
                Try Demo Account
              </Button>
            </div>
          </form>
        </Form>

        <Card className="p-4 mt-4 bg-muted/30">
          <h4 className="font-semibold mb-2 text-sm">Demo Credentials:</h4>
          <div className="text-sm text-muted-foreground space-y-1">
            <div>Email: demo@nexora.com</div>
            <div>Password: demo123</div>
          </div>
        </Card>

        <div className="text-center text-sm text-muted-foreground">
          Don't have an account?{' '}
          <Button variant="link" className="p-0 h-auto text-teal-accent">
            Sign up for free
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}