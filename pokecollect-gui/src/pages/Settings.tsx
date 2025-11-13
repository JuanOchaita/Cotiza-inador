import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, User, Bell, DollarSign, Shield, Globe } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const Settings = () => {
  const navigate = useNavigate();
  const { language, setLanguage, t } = useLanguage();
  const [settings, setSettings] = useState({
    email: "user@example.com",
    defaultExchangeRate: "7.75",
    notifications: true,
    priceAlerts: false,
    autoUpdate: true,
  });

  const handleSave = () => {
    console.log("Settings saved:", settings);
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/dashboard")}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <h1 className="text-2xl font-bold bg-gradient-pokemon bg-clip-text text-transparent">
              {t("settings.title")}
            </h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="space-y-6 animate-fade-in">
          {/* Account Settings */}
          <div className="bg-card rounded-lg border p-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <User className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{t("settings.account")}</h2>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">{t("settings.email")}</Label>
              <Input
                id="email"
                type="email"
                value={settings.email}
                onChange={(e) =>
                  setSettings({ ...settings, email: e.target.value })
                }
              />
            </div>
            <Button variant="outline" className="w-full">
              {t("settings.changePassword")}
            </Button>
          </div>

          {/* Language Settings */}
          <div className="bg-card rounded-lg border p-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{t("settings.language")}</h2>
            </div>
            <div className="space-y-2">
              <Label htmlFor="language">{t("settings.appLanguage")}</Label>
              <Select
                value={language}
                onValueChange={(value: "EN" | "ES") => setLanguage(value)}
              >
                <SelectTrigger id="language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="EN">English</SelectItem>
                  <SelectItem value="ES">Español</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                {t("settings.selectLanguage")}
              </p>
            </div>
          </div>

          {/* Currency Settings */}
          <div className="bg-card rounded-lg border p-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <DollarSign className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{t("settings.currency")}</h2>
            </div>
            <div className="space-y-2">
              <Label htmlFor="exchangeRate">{t("settings.exchangeRate")}</Label>
              <Input
                id="exchangeRate"
                type="number"
                step="0.01"
                min="7.0"
                max="8.0"
                value={settings.defaultExchangeRate}
                onChange={(e) =>
                  setSettings({ ...settings, defaultExchangeRate: e.target.value })
                }
              />
              <p className="text-sm text-muted-foreground">
                {t("settings.exchangeRateDesc")}
              </p>
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-card rounded-lg border p-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Bell className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{t("settings.notifications")}</h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t("settings.emailNotifications")}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t("settings.emailNotificationsDesc")}
                  </p>
                </div>
                <Switch
                  checked={settings.notifications}
                  onCheckedChange={(checked) =>
                    setSettings({ ...settings, notifications: checked })
                  }
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t("settings.priceAlerts")}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t("settings.priceAlertsDesc")}
                  </p>
                </div>
                <Switch
                  checked={settings.priceAlerts}
                  onCheckedChange={(checked) =>
                    setSettings({ ...settings, priceAlerts: checked })
                  }
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>{t("settings.autoUpdate")}</Label>
                  <p className="text-sm text-muted-foreground">
                    {t("settings.autoUpdateDesc")}
                  </p>
                </div>
                <Switch
                  checked={settings.autoUpdate}
                  onCheckedChange={(checked) =>
                    setSettings({ ...settings, autoUpdate: checked })
                  }
                />
              </div>
            </div>
          </div>

          {/* Privacy & Security */}
          <div className="bg-card rounded-lg border p-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{t("settings.privacy")}</h2>
            </div>
            <Button variant="outline" className="w-full">
              {t("settings.exportData")}
            </Button>
            <Button variant="destructive" className="w-full">
              {t("settings.deleteAccount")}
            </Button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button onClick={handleSave} className="flex-1">
              {t("settings.save")}
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => navigate("/dashboard")}
            >
              {t("settings.cancel")}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;
