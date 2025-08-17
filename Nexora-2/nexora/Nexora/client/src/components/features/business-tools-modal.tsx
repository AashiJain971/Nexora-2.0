import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  TrendingUp, 
  ShoppingCart, 
  Users, 
  Receipt, 
  FileText, 
  Download 
} from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';

interface BusinessToolsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BusinessToolsModal({ open, onOpenChange }: BusinessToolsModalProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const { 
    orders, 
    customers, 
    expenses, 
    recentExpenses 
  } = useDummyData();

  const formatCurrency = (amount: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(parseInt(amount));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'bg-green-accent/20 text-green-accent';
      case 'processing':
        return 'bg-orange-accent/20 text-orange-accent';
      case 'shipped':
        return 'bg-teal-accent/20 text-teal-accent';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const totalRevenue = 845230;
  const activeOrders = 23;
  const totalCustomers = 156;
  const totalExpenses = 234567;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-7xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Business Management Dashboard</DialogTitle>
        </DialogHeader>
        
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground">Total Sales</span>
              <TrendingUp className="w-5 h-5 text-green-accent" />
            </div>
            <div className="text-2xl font-bold text-green-accent">
              {formatCurrency(totalRevenue.toString())}
            </div>
            <div className="text-sm text-green-accent">↗ +12.5% from last month</div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground">Active Orders</span>
              <ShoppingCart className="w-5 h-5 text-orange-accent" />
            </div>
            <div className="text-2xl font-bold text-orange-accent">{activeOrders}</div>
            <div className="text-sm text-orange-accent">4 pending delivery</div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground">Customers</span>
              <Users className="w-5 h-5 text-teal-accent" />
            </div>
            <div className="text-2xl font-bold text-teal-accent">{totalCustomers}</div>
            <div className="text-sm text-teal-accent">8 new this week</div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground">Expenses</span>
              <Receipt className="w-5 h-5 text-red-400" />
            </div>
            <div className="text-2xl font-bold text-red-400">
              {formatCurrency(totalExpenses.toString())}
            </div>
            <div className="text-sm text-red-400">↗ +5.2% from last month</div>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="customers">Customers</TabsTrigger>
            <TabsTrigger value="expenses">Expenses</TabsTrigger>
          </TabsList>
          
          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Sales Chart */}
              <Card className="p-6">
                <h4 className="font-semibold mb-4">Monthly Sales Trend</h4>
                <div className="h-48 flex items-end justify-center space-x-2">
                  {[60, 80, 70, 90, 85, 95].map((height, index) => (
                    <div
                      key={index}
                      className="bg-teal-accent rounded-t flex-1 max-w-12"
                      style={{ height: `${height}%` }}
                    />
                  ))}
                </div>
                <div className="flex justify-between text-sm text-muted-foreground mt-2">
                  <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
                </div>
              </Card>
              
              {/* Top Products */}
              <Card className="p-6">
                <h4 className="font-semibold mb-4">Top Products</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Wooden Chairs</span>
                    <span className="text-green-accent font-semibold">₹2,45,000</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Spice Mix</span>
                    <span className="text-green-accent font-semibold">₹1,89,000</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Cotton Fabrics</span>
                    <span className="text-green-accent font-semibold">₹1,56,000</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Sensor Kits</span>
                    <span className="text-green-accent font-semibold">₹1,45,000</span>
                  </div>
                </div>
              </Card>
            </div>
          </TabsContent>
          
          {/* Orders Tab */}
          <TabsContent value="orders" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Recent Orders</h3>
              <Button size="sm" variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
            
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-4 py-3 text-left">Order ID</th>
                      <th className="px-4 py-3 text-left">Customer</th>
                      <th className="px-4 py-3 text-left">Product</th>
                      <th className="px-4 py-3 text-left">Amount</th>
                      <th className="px-4 py-3 text-left">Status</th>
                      <th className="px-4 py-3 text-left">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {orders.map((order) => (
                      <tr key={order.id} className="hover:bg-muted/25 transition-colors">
                        <td className="px-4 py-3 font-mono text-sm">{order.id}</td>
                        <td className="px-4 py-3">{order.customer}</td>
                        <td className="px-4 py-3">{order.product}</td>
                        <td className="px-4 py-3 font-semibold">
                          {formatCurrency(order.amount)}
                        </td>
                        <td className="px-4 py-3">
                          <Badge className={getStatusColor(order.status)}>
                            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {order.date}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </TabsContent>
          
          {/* Customers Tab */}
          <TabsContent value="customers" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Customer Directory</h3>
              <Button size="sm" variant="outline">
                <Users className="w-4 h-4 mr-2" />
                Add Customer
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {customers.map((customer) => (
                <Card key={customer.id} className="p-4">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-10 h-10 bg-teal-accent rounded-full flex items-center justify-center text-background font-semibold">
                      {customer.avatar}
                    </div>
                    <div>
                      <div className="font-semibold">{customer.name}</div>
                      <div className="text-sm text-muted-foreground">{customer.email}</div>
                    </div>
                  </div>
                  <div className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span>Total Orders:</span>
                      <span className="font-semibold">{customer.orders}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Total Spent:</span>
                      <span className="font-semibold text-green-accent">
                        {formatCurrency(customer.totalSpent)}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>
          
          {/* Expenses Tab */}
          <TabsContent value="expenses" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Expense Categories */}
              <Card className="p-6">
                <h4 className="font-semibold mb-4">Expense Categories</h4>
                <div className="space-y-3">
                  {expenses.map((expense) => (
                    <div key={expense.category} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full bg-${expense.color}-accent`} />
                        <span>{expense.category}</span>
                      </div>
                      <span className="font-semibold">{formatCurrency(expense.amount)}</span>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Recent Expenses */}
              <Card className="p-6">
                <h4 className="font-semibold mb-4">Recent Expenses</h4>
                <div className="space-y-3">
                  {recentExpenses.map((expense, index) => (
                    <div key={index} className="flex items-center justify-between py-2 border-b border-border">
                      <div>
                        <div className="font-medium">{expense.name}</div>
                        <div className="text-sm text-muted-foreground">{expense.date}</div>
                      </div>
                      <span className="text-red-400 font-semibold">
                        -{formatCurrency(expense.amount)}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card className="p-6">
              <h4 className="font-semibold mb-4">Quick Actions</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button className="justify-start" variant="outline">
                  <FileText className="w-4 h-4 mr-2" />
                  Add Expense
                </Button>
                <Button className="justify-start" variant="outline">
                  <Receipt className="w-4 h-4 mr-2" />
                  Generate Invoice
                </Button>
                <Button className="justify-start" variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export Reports
                </Button>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
