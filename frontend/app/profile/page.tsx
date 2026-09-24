"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { PageSpinner } from "@/components/ui/states";
import { useRequireAuth } from "@/lib/auth";
import { authApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { User } from "@/types";

export default function ProfilePage() {
  const { user, loading: authLoading, setUser } = useRequireAuth();

  if (authLoading || !user) return <PageSpinner />;

  return (
    <AppShell>
      <div className="mx-auto max-w-2xl space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Profile</h1>
          <p className="mt-1 text-muted-foreground">Keep this up to date — it helps tailor recommendations.</p>
        </div>
        <ProfileForm user={user} onSaved={setUser} />
      </div>
    </AppShell>
  );
}

// A separate component so its field state can be initialized directly from
// `user` (a stable prop by the time this ever mounts, since the page above
// only renders it once `user` is non-null) — no effect needed to sync state.
function ProfileForm({ user, onSaved }: { user: User; onSaved: (user: User) => void }) {
  const [fullName, setFullName] = useState(user.full_name ?? "");
  const [location, setLocation] = useState(user.location ?? "");
  const [githubUrl, setGithubUrl] = useState(user.github_url ?? "");
  const [linkedinUrl, setLinkedinUrl] = useState(user.linkedin_url ?? "");
  const [portfolioUrl, setPortfolioUrl] = useState(user.portfolio_url ?? "");
  const [preferredRole, setPreferredRole] = useState(user.preferred_role ?? "");
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await authApi.updateProfile({
        full_name: fullName || null,
        location: location || null,
        github_url: githubUrl || null,
        linkedin_url: linkedinUrl || null,
        portfolio_url: portfolioUrl || null,
        preferred_role: preferredRole || null,
      });
      onSaved(updated);
      toast.success("Profile updated.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="profile-email">Email</Label>
          <Input id="profile-email" value={user.email} disabled />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="profile-name">Full name</Label>
            <Input id="profile-name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="profile-location">Location</Label>
            <Input id="profile-location" value={location} onChange={(e) => setLocation(e.target.value)} />
          </div>
        </div>
        <div>
          <Label htmlFor="profile-role">Preferred job role</Label>
          <Input
            id="profile-role"
            value={preferredRole}
            onChange={(e) => setPreferredRole(e.target.value)}
            placeholder="e.g. Backend Engineer"
          />
        </div>
        <div>
          <Label htmlFor="profile-github">GitHub</Label>
          <Input id="profile-github" type="url" value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="profile-linkedin">LinkedIn</Label>
          <Input
            id="profile-linkedin"
            type="url"
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="profile-portfolio">Portfolio</Label>
          <Input
            id="profile-portfolio"
            type="url"
            value={portfolioUrl}
            onChange={(e) => setPortfolioUrl(e.target.value)}
          />
        </div>
        <Button onClick={handleSave} loading={saving}>
          Save changes
        </Button>
      </CardContent>
    </Card>
  );
}
