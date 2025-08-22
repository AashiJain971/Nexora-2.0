import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Store, User, Camera, MessageCircle, Loader2 } from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';
import { useToast } from '@/hooks/use-toast';

interface MarketplaceModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MarketplaceModal({ open, onOpenChange }: MarketplaceModalProps) {
  const [activeTab, setActiveTab] = useState('browse');
  const [isListing, setIsListing] = useState(false);
  const [listingForm, setListingForm] = useState({
    name: '',
    category: '',
    description: '',
    price: '',
    minOrder: '',
    stock: '',
  });
  
  const { marketplaceProducts, buyerInquiries, simulateProductListing } = useDummyData();
  const { toast } = useToast();

  const handleInputChange = (field: string, value: string) => {
    setListingForm(prev => ({ ...prev, [field]: value }));
  };

  const handleProductListing = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsListing(true);
    
    try {
      const result = await simulateProductListing(listingForm);
      if (result.success) {
        toast({
          title: "Product's best marketplace is anlaysed",
          description: `Best market place for your product ${listingForm.name} will be _______ `,
        });
        
        // Reset form
        setListingForm({
          name: '',
          category: '',
          description: '',
          price: '',
          minOrder: '',
          stock: '',
        });
      }
    } catch (error) {
      toast({
        title: "Listing Failed",
        description: "Failed to list product. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsListing(false);
    }
  };

  const contactSeller = (productId: string) => {
    toast({
      title: "Contact Details Sent!",
      description: "The seller's contact information has been sent to your email.",
    });
  };

  const formatCurrency = (amount: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(parseInt(amount));
  };

  const getMatchColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-accent/20 text-green-accent';
    if (percentage >= 80) return 'bg-orange-accent/20 text-orange-accent';
    return 'bg-muted text-muted-foreground';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Product Marketplace & Buyer Matching</DialogTitle>
        </DialogHeader>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="browse">Browse Products</TabsTrigger>
            <TabsTrigger value="list">List Product</TabsTrigger>
          </TabsList>
          
          {/* Browse Products Tab */}
          <TabsContent value="browse" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {marketplaceProducts.map((product) => (
                <Card key={product.id} className="overflow-hidden hover:border-teal-accent/50 transition-colors">
                  <img
                    src={`${product.image}?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=400&h=250`}
                    alt={product.name}
                    className="w-full h-40 object-cover"
                  />
                  <div className="p-4">
                    <h4 className="font-semibold mb-2">{product.name}</h4>
                    <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                      {product.description}
                    </p>
                    
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-lg font-bold text-green-accent">
                        {formatCurrency(product.price)}/piece
                      </span>
                      <span className="text-sm text-muted-foreground">
                        Min. {product.minOrder} pieces
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1 text-sm">
                        <User className="w-4 h-4 text-teal-accent" />
                        <span>{product.seller}</span>
                      </div>
                      <Button
                        onClick={() => contactSeller(product.id)}
                        size="sm"
                        className="bg-teal-accent hover:bg-teal-accent/90"
                      >
                        Contact
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Buyer Inquiries Section */}
            <div className="mt-8">
              <h3 className="text-xl font-semibold mb-4">Recent Buyer Inquiries</h3>
              <div className="space-y-4">
                {buyerInquiries.map((inquiry) => (
                  <Card key={inquiry.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-teal-accent rounded-full flex items-center justify-center text-background font-semibold">
                          {inquiry.avatar}
                        </div>
                        <div>
                          <h4 className="font-semibold">{inquiry.buyerName}</h4>
                          <p className="text-sm text-muted-foreground">
                            Interested in {inquiry.productName} • Quantity: {inquiry.quantity} units
                          </p>
                          {inquiry.message && (
                            <p className="text-sm text-muted-foreground mt-1">
                              "{inquiry.message}"
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge className={getMatchColor(inquiry.matchPercentage)}>
                          {inquiry.matchPercentage}% Match
                        </Badge>
                        <Button size="sm" className="bg-teal-accent hover:bg-teal-accent/90">
                          <MessageCircle className="w-4 h-4 mr-1" />
                          Respond
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>
          
          {/* List Product Tab */}
          <TabsContent value="list" className="space-y-6">
            <form onSubmit={handleProductListing} className="max-w-2xl mx-auto space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="productName">Product Name</Label>
                  <Input
                    id="productName"
                    placeholder="Enter product name"
                    value={listingForm.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="category">Category</Label>
                  <Select value={listingForm.category} onValueChange={(value) => handleInputChange('category', value)} required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="furniture">Furniture</SelectItem>
                      <SelectItem value="textiles">Textiles</SelectItem>
                      <SelectItem value="food">Food & Beverages</SelectItem>
                      <SelectItem value="handicrafts">Handicrafts</SelectItem>
                      <SelectItem value="electronics">Electronics</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <Label htmlFor="description">Product Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe your product..."
                  value={listingForm.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={4}
                  required
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="price">Price per Unit (₹)</Label>
                  <Input
                    id="price"
                    type="number"
                    placeholder="0"
                    value={listingForm.price}
                    onChange={(e) => handleInputChange('price', e.target.value)}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="minOrder">Minimum Order</Label>
                  <Input
                    id="minOrder"
                    type="number"
                    placeholder="1"
                    value={listingForm.minOrder}
                    onChange={(e) => handleInputChange('minOrder', e.target.value)}
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="stock">Available Stock</Label>
                  <Input
                    id="stock"
                    type="number"
                    placeholder="1000"
                    value={listingForm.stock}
                    onChange={(e) => handleInputChange('stock', e.target.value)}
                    required
                  />
                </div>
              </div>
              
              <div>
                <Label>Product Images</Label>
                <Card className="border-2 border-dashed border-border p-6 text-center hover:border-teal-accent transition-colors cursor-pointer">
                  <Camera className="w-8 h-8 text-teal-accent mx-auto mb-2" />
                  <p className="text-muted-foreground">Upload product images (up to 5)</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Drag & drop files here or click to browse
                  </p>
                </Card>
              </div>
              
              <Button
                type="submit"
                disabled={isListing}
                className="w-full bg-gradient-to-r from-teal-accent to-green-accent"
              >
                {isListing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analysing best amrketplace for you...
                  </>
                ) : (
                  <>
                    <Store className="w-4 h-4 mr-2" />
                    Find best market for your product
                  </>
                )}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
