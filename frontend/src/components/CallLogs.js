import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Search, Phone, Clock, Filter, Calendar } from 'lucide-react';
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

const dispositionColors = {
  interested: 'bg-green-100 text-green-800',
  not_interested: 'bg-red-100 text-red-800',
  callback: 'bg-blue-100 text-blue-800',
  follow_up: 'bg-yellow-100 text-yellow-800',
  busy: 'bg-orange-100 text-orange-800',
  voicemail: 'bg-purple-100 text-purple-800'
};

const CallLogs = () => {
  const [callLogs, setCallLogs] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [dispositionFilter, setDispositionFilter] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    contact_id: '',
    contact_name: '',
    date: '',
    duration: 0,
    outcome: '',
    notes: '',
    disposition: 'interested',
    follow_up_date: ''
  });
  
  useEffect(() => {
    fetchCallLogs();
    fetchContacts();
  }, []);
  
  const fetchCallLogs = async () => {
    try {
      const response = await axios.get(`${API}/call-logs`);
      setCallLogs(response.data);
    } catch (error) {
      console.error('Error fetching call logs:', error);
      toast.error('Failed to load call logs');
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
        date: new Date(formData.date).toISOString(),
        follow_up_date: formData.follow_up_date ? new Date(formData.follow_up_date).toISOString() : null
      };
      
      await axios.post(`${API}/call-logs`, submitData);
      toast.success('Call log created successfully');
      setIsAddDialogOpen(false);
      fetchCallLogs();
      resetForm();
    } catch (error) {
      console.error('Error saving call log:', error);
      toast.error('Failed to save call log');
    }
  };
  
  const resetForm = () => {
    setFormData({
      contact_id: '',
      contact_name: '',
      date: '',
      duration: 0,
      outcome: '',
      notes: '',
      disposition: 'interested',
      follow_up_date: ''
    });
  };
  
  // Filter call logs
  const filteredCallLogs = callLogs.filter(log => {
    const matchesSearch = log.contact_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.outcome.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDisposition = dispositionFilter === 'all' || log.disposition === dispositionFilter;
    return matchesSearch && matchesDisposition;
  });
  
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse" data-testid="call-logs-loading">
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
    <div className="space-y-6" data-testid="call-logs-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Call Logs</h1>
          <p className="text-gray-600 mt-1">Track your business calls and outcomes</p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={resetForm} data-testid="add-call-log-btn">
              <Plus className="w-4 h-4 mr-2" />
              Log Call
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Log New Call</DialogTitle>
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
                  <Label htmlFor="date">Call Date *</Label>
                  <Input
                    id="date"
                    type="datetime-local"
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="duration">Duration (minutes) *</Label>
                  <Input
                    id="duration"
                    type="number"
                    min="0"
                    value={formData.duration}
                    onChange={(e) => setFormData({...formData, duration: parseInt(e.target.value) || 0})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="disposition">Call Disposition *</Label>
                  <Select 
                    value={formData.disposition} 
                    onValueChange={(value) => setFormData({...formData, disposition: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="interested">Interested</SelectItem>
                      <SelectItem value="not_interested">Not Interested</SelectItem>
                      <SelectItem value="callback">Callback Required</SelectItem>
                      <SelectItem value="follow_up">Follow Up</SelectItem>
                      <SelectItem value="busy">Busy</SelectItem>
                      <SelectItem value="voicemail">Voicemail</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div>
                <Label htmlFor="outcome">Call Outcome *</Label>
                <Input
                  id="outcome"
                  value={formData.outcome}
                  onChange={(e) => setFormData({...formData, outcome: e.target.value})}
                  placeholder="Brief summary of the call outcome"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="follow_up_date">Follow-up Date</Label>
                <Input
                  id="follow_up_date"
                  type="datetime-local"
                  value={formData.follow_up_date}
                  onChange={(e) => setFormData({...formData, follow_up_date: e.target.value})}
                />
              </div>
              
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  placeholder="Detailed notes about the call..."
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
                <Button type="submit" data-testid="save-call-log-btn">
                  Save Call Log
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
                  placeholder="Search call logs by contact name or outcome..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                  data-testid="search-call-logs"
                />
              </div>
            </div>
            <Select value={dispositionFilter} onValueChange={setDispositionFilter}>
              <SelectTrigger className="w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by disposition" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Dispositions</SelectItem>
                <SelectItem value="interested">Interested</SelectItem>
                <SelectItem value="not_interested">Not Interested</SelectItem>
                <SelectItem value="callback">Callback</SelectItem>
                <SelectItem value="follow_up">Follow Up</SelectItem>
                <SelectItem value="busy">Busy</SelectItem>
                <SelectItem value="voicemail">Voicemail</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      {/* Call Logs List */}
      {filteredCallLogs.length === 0 ? (
        <Card data-testid="no-call-logs">
          <CardContent className="p-8 text-center">
            <Phone className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No call logs found</h3>
            <p className="text-gray-600 mb-4">Start tracking your calls by logging your first call.</p>
            <Button onClick={() => setIsAddDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Log Call
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredCallLogs.map((log) => {
            const callDate = new Date(log.date);
            const followUpDate = log.follow_up_date ? new Date(log.follow_up_date) : null;
            
            return (
              <Card key={log.id} className="hover:shadow-md transition-shadow" data-testid="call-log-card">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="p-2 bg-blue-50 rounded-lg">
                          <Phone className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">{log.contact_name}</h3>
                          <p className="text-sm text-gray-600">{log.outcome}</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{format(callDate, 'MMM dd, yyyy HH:mm')}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="w-4 h-4 mr-2" />
                          <span>{log.duration} minutes</span>
                        </div>
                        <div className="flex items-center">
                          <Badge className={dispositionColors[log.disposition] || 'bg-gray-100 text-gray-800'}>
                            {log.disposition.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      
                      {log.notes && (
                        <p className="text-sm text-gray-700 mt-3 bg-gray-50 p-3 rounded-lg">
                          {log.notes}
                        </p>
                      )}
                      
                      {followUpDate && (
                        <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                          <p className="text-sm text-yellow-800">
                            <strong>Follow-up scheduled:</strong> {format(followUpDate, 'MMM dd, yyyy HH:mm')}
                          </p>
                        </div>
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

export default CallLogs;
