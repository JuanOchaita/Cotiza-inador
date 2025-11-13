import { useState, useEffect } from "react";
import { Plus, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import CollectionCard from "@/components/CollectionCard";
import { useLanguage } from "@/contexts/LanguageContext";
import { formatNumber } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { getCollectionsByUser, Collection } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";

const Dashboard = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate("/");
      return;
    }

    const fetchCollections = async () => {
      try {
        const data = await getCollectionsByUser(user.user_id);
        setCollections(data);
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch collections",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCollections();
  }, [user, navigate, toast]);

  const formatCurrency = (usd: number, exchangeRate: number) => {
    const gtq = usd * exchangeRate;
    return {
      gtq: formatNumber(gtq),
      usd: formatNumber(usd),
    };
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-pokemon bg-clip-text text-transparent">
            {t("app.title")}
          </h1>
          <div className="flex items-center gap-3">
            <Button className="gap-2" onClick={() => navigate("/add-collection")}>
              <Plus className="h-4 w-4" />
              {t("nav.addCollection")}
            </Button>
            <Button variant="outline" size="icon" onClick={() => navigate("/settings")}>
              <Settings className="h-5 w-5" />
            </Button>
            <Button variant="outline" onClick={handleLogout}>
              {t("nav.logout")}
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {collections.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
            <div className="text-center space-y-4 max-w-md">
              <h2 className="text-3xl font-bold text-foreground">{t("dashboard.noCollections")}</h2>
              <p className="text-muted-foreground">
                {t("dashboard.noCollectionsDesc")}
              </p>
              <Button className="gap-2 mt-4" onClick={() => navigate("/add-collection")}>
                <Plus className="h-4 w-4" />
                {t("dashboard.createFirst")}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold">{t("dashboard.myCollections")}</h2>
              <p className="text-muted-foreground">
                {collections.length} {collections.length === 1 ? t("dashboard.collection") : t("dashboard.collections")}
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {collections.map((collection, index) => {
                const totalCards = 0; // Will be calculated from card quantities
                const mockCollection = {
                  id: String(collection.collection_id),
                  title: collection.title,
                  cards: [],
                  lastUpdated: new Date(collection.created_at).toLocaleDateString(),
                };
                
                // Create a mock card for display purposes with the total value
                const mockCards = [{
                  id: "total",
                  name: "",
                  setNumber: "",
                  setName: "",
                  condition: "NM" as const,
                  language: "EN" as const,
                  version: "",
                  valueUSD: collection.collection_price_usd,
                  lastUpdated: new Date(collection.created_at).toLocaleDateString(),
                  imageUrl: "",
                }];
                
                return (
                  <CollectionCard
                    key={collection.collection_id}
                    collection={{ ...mockCollection, cards: mockCards }}
                    exchangeRate={collection.exchange_rate}
                    formatCurrency={(usd) => formatCurrency(usd, collection.exchange_rate)}
                    onClick={() => navigate(`/collection/${collection.collection_id}`)}
                    style={{ animationDelay: `${index * 0.1}s` }}
                    className="animate-slide-up"
                  />
                );
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
