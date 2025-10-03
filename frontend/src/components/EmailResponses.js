import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Search, Mail, Filter, Calendar, Send } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { format } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const statusColors = {
  sent: 'bg-blue-100 text-blue-800',
  opened: 'bg-yellow-100 text-yellow-800',
  replied: 'bg-green-100 text-green-800',
  bounced: 'bg-red-100 text-red-800',
  no_response: 'bg-gray-100 text-gray-800'
};

const responseTypeColors = {
  positive: 'bg-green-100 text-green-800',
  negative: 'bg-red-100 text-red-800',
  neutral: 'bg-yellow-100 text-yellow-800'
};

const EmailResponses = () => {
  const [emailResponses, setEmailResponses] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    contact_id: '',
    contact_name: '',
    email_type: '',
    subject: '',
    date: '',
    status: 'sent',
    response_type: '',
    notes: ''
  });
  
  useEffect(() => {
    fetchEmailResponses();
    fetchContacts();
  }, []);
  
  const fetchEmailResponses = async () => {
    try {
      const response = await axios.get(`${API}/email-responses`);
      setEmailResponses(response.data);
    } catch (error) {
      console.error('Error fetching email responses:', error);
      toast.error('Failed to load email responses');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchContacts = async () => {
    try {
      const response = await axios.get(`${API}/contacts`);
      setContacts(response.data);
    } catch (error) {
      console.error('Error fetching contacts:', error);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const selectedContact = contacts.find(c => c.id === formData.contact_id);
      const submitData = {
        ...formData,
        contact_name: selectedContact?.name || formData.contact_name,
        date: new Date(formData.date).toISOString()
      };
      
      await axios.post(`${API}/email-responses`, submitData);
      toast.success('Email response logged successfully');
      setIsAddDialogOpen(false);
      fetchEmailResponses();
      resetForm();
    } catch (error) {
      console.error('Error saving email response:', error);
      toast.error('Failed to save email response');
    }
  };
  
  const resetForm = () => {
    setFormData({
      contact_id: '',
      contact_name: '',
      email_type: '',
      subject: '',
      date: '',
      status: 'sent',
      response_type: '',
      notes: ''
    });
  };
  
  // Filter email responses
  const filteredEmailResponses = emailResponses.filter(response => {
    const matchesSearch = response.contact_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         response.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         response.email_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || response.status === statusFilter;
    return matchesSearch && matchesStatus;
  });
  
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse" data-testid="email-responses-loading">
        <div className="flex justify-between items-center">
          <div className="h-8 bg-gray-200 rounded w-48"></div>
          <div className="h-10 bg-gray-200 rounded w-32"></div>
        </div>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-24"></div>
          ))}
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6" data-testid="email-responses-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Email Responses</h1>
          <p className="text-gray-600 mt-1">Track your business email communications</p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm} data-testid="add-email-response-btn">
              <Plus className="w-4 h-4 mr-2" />
              Log Email
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Log Email Response</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="contact_id">Contact *</Label>
                  <Select 
                    value={formData.contact_id} 
                    onValueChange={(value) => setFormData({...formData, contact_id: value})}
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select contact" />
                    </SelectTrigger>
                    <SelectContent>
                      {contacts.map(contact => (
                        <SelectItem key={contact.id} value={contact.id}>
                          {contact.name} - {contact.company}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="email_type">Email Type *</Label>
                  <Select 
                    value={formData.email_type} 
                    onValueChange={(value) => setFormData({...formData, email_type: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="outreach">Initial Outreach</SelectItem>
                      <SelectItem value="follow_up">Follow Up</SelectItem>
                      <SelectItem value="proposal">Proposal</SelectItem>
                      <SelectItem value="meeting_request">Meeting Request</SelectItem>
                      <SelectItem value="thank_you">Thank You</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <Label htmlFor="subject">Email Subject *</Label>
                <Input
                  id="subject"
                  value={formData.subject}
                  onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  placeholder="Email subject line"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date">Email Date *</Label>
                  <Input
                    id="date"
                    type="datetime-local"
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="status">Status *</Label>
                  <Select 
                    value={formData.status} 
                    onValueChange={(value) => setFormData({...formData, status: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sent">Sent</SelectItem>
                      <SelectItem value="opened">Opened</SelectItem>
                      <SelectItem value="replied">Replied</SelectItem>
                      <SelectItem value="bounced">Bounced</SelectItem>
                      <SelectItem value="no_response">No Response</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <Label htmlFor="response_type">Response Type</Label>
                <Select 
                  value={formData.response_type} 
                  onValueChange={(value) => setFormData({...formData, response_type: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select response type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="positive">Positive</SelectItem>
                    <SelectItem value="negative">Negative</SelectItem>
                    <SelectItem value="neutral">Neutral</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  placeholder="Details about the email response..."
                  rows={3}
                />
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsAddDialogOpen(false);
                    resetForm();
                  }}
                >
                  Cancel
                </Button>
                <Button type="submit" data-testid="save-email-response-btn">
                  Save Email Response
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
      
      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search by contact name, subject, or email type..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                  data-testid="search-email-responses"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="opened">Opened</SelectItem>
                <SelectItem value="replied">Replied</SelectItem>
                <SelectItem value="bounced">Bounced</SelectItem>
                <SelectItem value="no_response">No Response</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      {/* Email Responses List */}
      {filteredEmailResponses.length === 0 ? (
        <Card data-testid="no-email-responses">
          <CardContent className="p-8 text-center">
            <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No email responses found</h3>
            <p className="text-gray-600 mb-4">Start tracking your email outreach by logging your first email.</p>
            <Button onClick={() => setIsAddDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Log Email
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredEmailResponses.map((response) => {
            const emailDate = new Date(response.date);
            
            return (
              <Card key={response.id} className="hover:shadow-md transition-shadow" data-testid="email-response-card">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-purple-50 rounded-lg">
                          <Mail className="w-5 h-5 text-purple-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">{response.contact_name}</h3>
                          <p className="text-base text-gray-800 font-medium">{response.subject}</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Send className="w-4 h-4 mr-2" />
                          <span className="capitalize">{response.email_type.replace('_', ' ')}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{format(emailDate, 'MMM dd, yyyy HH:mm')}</span>
                        </div>
                        <div className="flex items-center">
                          <Badge className={statusColors[response.status] || 'bg-gray-100 text-gray-800'}>
                            {response.status.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                        {response.response_type && (
                          <div className="flex items-center">
                            <Badge className={responseTypeColors[response.response_type] || 'bg-gray-100 text-gray-800'}>
                              {response.response_type.toUpperCase()}
                            </Badge>
                          </div>
                        )}
                      </div>
                      
                      {response.notes && (
                        <p className="text-sm text-gray-700 mt-3 bg-gray-50 p-3 rounded-lg">
                          {response.notes}
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default EmailResponses;
