import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Bot, User, Send } from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface AIChatbotProps {
  className?: string;
}

export function AIChatbot({ className }: AIChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm your AI business assistant. I can help you with marketing strategies, financial planning, supply chain optimization, and more. What would you like to know?",
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { getRandomAIResponse } = useDummyData();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: getRandomAIResponse(),
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const quickQuestions = [
    "How to improve my credit score?",
    "Best marketing strategies for my business?",
    "What loans am I eligible for?",
    "How to optimize my supply chain?",
  ];

  return (
    <Card className={`p-6 ${className}`}>
      <div className="flex items-center space-x-2 mb-4">
        <Bot className="w-5 h-5 text-teal-accent" />
        <h4 className="text-lg font-semibold">AI Business Assistant</h4>
      </div>
      
      <div className="h-80 overflow-y-auto mb-4 space-y-3 bg-muted/50 rounded-lg p-3">
        {messages.map((message) => (
          <div key={message.id} className="flex items-start space-x-2">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
              message.sender === 'ai' 
                ? 'bg-teal-accent text-background' 
                : 'bg-orange-accent text-background'
            }`}>
              {message.sender === 'ai' ? (
                <Bot className="w-3 h-3" />
              ) : (
                <User className="w-3 h-3" />
              )}
            </div>
            <div className={`rounded-lg p-2 text-sm max-w-xs ${
              message.sender === 'ai'
                ? 'bg-teal-accent/10 text-foreground'
                : 'bg-orange-accent/10 text-foreground'
            }`}>
              {message.content}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex items-start space-x-2">
            <div className="w-6 h-6 bg-teal-accent rounded-full flex items-center justify-center">
              <Bot className="w-3 h-3 text-background" />
            </div>
            <div className="bg-teal-accent/10 rounded-lg p-2 text-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-teal-accent rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-teal-accent rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-teal-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex space-x-2 mb-3">
        <Input
          type="text"
          placeholder="Ask me anything about your business..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          className="flex-1"
        />
        <Button onClick={sendMessage} size="icon" className="bg-teal-accent hover:bg-teal-accent/90">
          <Send className="w-4 h-4" />
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {quickQuestions.map((question) => (
          <Button
            key={question}
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => {
              setInputValue(question);
              setTimeout(() => sendMessage(), 100);
            }}
          >
            {question}
          </Button>
        ))}
      </div>
    </Card>
  );
}
