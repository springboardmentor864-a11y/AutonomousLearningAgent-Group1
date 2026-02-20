import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { User, Mail, Phone, Loader2, Save } from 'lucide-react';

const Profile = () => {
  const { profile, user, refreshProfile } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || '',
    phone: profile?.phone || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsLoading(true);
    const { error } = await supabase
      .from('profiles')
      .update({
        full_name: formData.full_name,
        phone: formData.phone,
      })
      .eq('user_id', user.id);

    setIsLoading(false);

    if (error) {
      toast({
        title: 'Update failed',
        description: error.message,
        variant: 'destructive',
      });
    } else {
      await refreshProfile();
      toast({
        title: 'Profile updated',
        description: 'Your profile has been successfully updated.',
      });
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-serif font-bold text-foreground mb-2">Profile</h1>
        <p className="text-muted-foreground">Manage your personal information</p>
      </div>

      {/* Profile Card */}
      <Card className="border-0 shadow-lg">
        <CardHeader className="text-center pb-6">
          <div className="w-24 h-24 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl font-serif font-bold text-accent">
              {profile?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </span>
          </div>
          <CardTitle className="text-2xl font-serif">{profile?.full_name || 'User'}</CardTitle>
          <CardDescription>{profile?.email}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="full_name" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Full Name
              </Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="Enter your full name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Email
              </Label>
              <Input
                id="email"
                type="email"
                value={profile?.email || ''}
                disabled
                className="bg-muted"
              />
              <p className="text-xs text-muted-foreground">Email cannot be changed</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone" className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                Phone Number
              </Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="Enter your phone number"
              />
            </div>

            <Button type="submit" className="w-full bg-accent hover:bg-accent/90" disabled={isLoading}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Save Changes
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Account Info */}
      <Card className="border-0 shadow-lg">
        <CardHeader>
          <CardTitle className="font-serif">Account Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between py-3 border-b">
            <span className="text-muted-foreground">Member Since</span>
            <span className="font-medium">
              {profile?.created_at 
                ? new Date(profile.created_at).toLocaleDateString('en-US', { 
                    month: 'long', 
                    year: 'numeric' 
                  })
                : 'N/A'
              }
            </span>
          </div>
          <div className="flex justify-between py-3 border-b">
            <span className="text-muted-foreground">Account Status</span>
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-emerald/10 text-emerald">
              Active
            </span>
          </div>
          <div className="flex justify-between py-3">
            <span className="text-muted-foreground">Last Updated</span>
            <span className="font-medium">
              {profile?.updated_at 
                ? new Date(profile.updated_at).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric',
                    year: 'numeric' 
                  })
                : 'N/A'
              }
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
