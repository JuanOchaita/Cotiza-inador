import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  Layers,
  Plus,
  Upload,
  Share2,
  Download,
  Link2,
  Check,
  Trash2,
} from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import CardListItem from "@/components/CardListItem";
import { formatNumber } from "@/lib/utils";
import { apiRequest, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { ApiCollectionDetail, ApiCardItem } from "@/types/api";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

type NewCardForm = {
  name: string;
  setNumber: string;
  setName: string;
  condition: string;
  language: string;
  version: string;
  imageUrl: string;
  valueUsd: number;
  quantity: number;
};

const INITIAL_CARD_STATE: NewCardForm = {
  name: "",
  setNumber: "",
  setName: "",
  condition: "NM",
  language: "EN",
  version: "",
  imageUrl: "",
  valueUsd: 0,
  quantity: 1,
};

const CollectionDetail = () => {
  const { id } = useParams();
  const collectionId = Number(id);
  const navigate = useNavigate();
  const { token } = useAuth();

  const [exchangeRate, setExchangeRate] = useState(7.75);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [cardToDelete, setCardToDelete] = useState<number | null>(null);
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [urlCopied, setUrlCopied] = useState(false);
  const [newCard, setNewCard] = useState<NewCardForm>(INITIAL_CARD_STATE);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!Number.isFinite(collectionId)) {
      navigate("/dashboard", { replace: true });
    }
  }, [collectionId, navigate]);

  const { data, isLoading, refetch, error } = useQuery({
    queryKey: ["collection", collectionId],
    queryFn: () => apiRequest<ApiCollectionDetail>(`/collections/${collectionId}`, { token }),
    enabled: Boolean(token) && Number.isFinite(collectionId),
    retry: false,
  });

  const addCardMutation = useMutation({
    mutationFn: () =>
      apiRequest<ApiCardItem>(`/collections/${collectionId}/cards`, {
        method: "POST",
        token,
        body: {
          name: newCard.name,
          set_number: newCard.setNumber || null,
          set_name: newCard.setName || null,
          condition: newCard.condition,
          language: newCard.language,
          version: newCard.version || null,
          imageUrl: newCard.imageUrl || null,
          value_usd: Number.isFinite(newCard.valueUsd) ? newCard.valueUsd : 0,
          quantity: Number.isFinite(newCard.quantity) ? newCard.quantity : 1,
        },
      }),
    onSuccess: () => {
      setIsAddDialogOpen(false);
      setFormError(null);
      setNewCard(INITIAL_CARD_STATE);
      refetch();
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError) {
        setFormError(err.message);
      } else {
        setFormError("Error adding card.");
      }
    },
  });

  const deleteCardMutation = useMutation({
    mutationFn: (cardCollectionId: number) =>
      apiRequest(`/collections/${collectionId}/cards/${cardCollectionId}`, {
        method: "DELETE",
        token,
      }),
    onSuccess: () => {
      setCardToDelete(null);
      refetch();
    },
  });

  const cards = data?.cards ?? [];

  const formatCurrency = (usd: number) => {
    const gtq = usd * exchangeRate;
    return {
      gtq: formatNumber(gtq),
      usd: formatNumber(usd),
    };
  };

  const totals = useMemo(() => {
    const totalUsd = data?.total_value_usd ?? 0;
    const { gtq, usd } = formatCurrency(totalUsd);
    return { totalUsd, gtq, usd };
  }, [data?.total_value_usd, exchangeRate]);

  const handleDownloadPDF = () => {
    if (!data) return;
    const doc = new jsPDF();
    doc.setFontSize(20);
    doc.text(data.name, 14, 20);

    doc.setFontSize(12);
    doc.text(`Total Value: Q${totals.gtq} (USD $${totals.usd})`, 14, 30);
    doc.text(`Number of Cards: ${data.cards_count}`, 14, 37);
    doc.text(`Created: ${new Date(data.created_at).toLocaleDateString()}`, 14, 44);

    const tableData = cards.map((card) => {
      const currency = formatCurrency(card.value_usd ?? 0);
      return [
        card.name,
        card.set_number ?? "-",
        card.set_name ?? "-",
        card.condition,
        card.language,
        card.version ?? "-",
        `${card.quantity}`,
        `Q${currency.gtq}`,
        `$${currency.usd}`,
      ];
    });

    autoTable(doc, {
      head: [["Name", "Set #", "Set Name", "Condition", "Lang", "Version", "Qty", "GTQ", "USD"]],
      body: tableData,
      startY: 50,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [59, 130, 246] },
    });

    doc.save(`${data.name}.pdf`);
    setIsShareOpen(false);
  };

  const handleCopyURL = () => {
    const url = `${window.location.origin}/collection/${collectionId}`;
    navigator.clipboard.writeText(url);
    setUrlCopied(true);
    setTimeout(() => setUrlCopied(false), 2000);
  };

  const handleAddCard = () => {
    if (!newCard.name.trim()) {
      setFormError("Card name is required.");
      return;
    }
    if (newCard.quantity < 1) {
      setFormError("Quantity must be at least 1.");
      return;
    }
    addCardMutation.mutate();
  };

  const handleDeleteCard = () => {
    if (!cardToDelete) return;
    deleteCardMutation.mutate(cardToDelete);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading collection...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">Collection not found</h2>
          <Button onClick={() => navigate("/dashboard")}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <Button variant="ghost" onClick={() => navigate("/dashboard")} className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Collections
            </Button>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium">Exchange Rate:</label>
              <Select
                value={exchangeRate.toString()}
                onValueChange={(value) => setExchangeRate(parseFloat(value))}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 11 }, (_, i) => (7.0 + i * 0.1).toFixed(1)).map((rate) => (
                    <SelectItem key={rate} value={rate}>
                      {rate}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="bg-gradient-card rounded-lg p-6 shadow-card mb-8 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold">{data.name}</h1>
            <div className="flex gap-2">
              <Popover open={isShareOpen} onOpenChange={setIsShareOpen}>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="gap-2">
                    <Share2 className="h-4 w-4" />
                    Share
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-80">
                  <div className="space-y-3">
                    <h3 className="font-semibold text-sm">Share Collection</h3>
                    <Button variant="outline" className="w-full justify-start gap-2" onClick={handleDownloadPDF}>
                      <Download className="h-4 w-4" />
                      Download PDF
                    </Button>
                    <div className="space-y-2">
                      <div className="flex gap-2">
                        <Input readOnly value={`${window.location.origin}/collection/${collectionId}`} className="text-xs" />
                        <Button variant="outline" size="icon" onClick={handleCopyURL}>
                          {urlCopied ? <Check className="h-4 w-4 text-green-500" /> : <Link2 className="h-4 w-4" />}
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">Get shareable URL</p>
                    </div>
                  </div>
                </PopoverContent>
              </Popover>
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="gap-2">
                    <Plus className="h-4 w-4" />
                    Add Card
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Add Card to Collection</DialogTitle>
                    <DialogDescription>Add a single card or upload multiple cards via file.</DialogDescription>
                  </DialogHeader>
                  <Tabs defaultValue="single" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="single">Add Single Card</TabsTrigger>
                      <TabsTrigger value="multiple">Add Multiple Cards</TabsTrigger>
                    </TabsList>
                    <TabsContent value="single" className="space-y-4 mt-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="name">Card Name</Label>
                          <Input
                            id="name"
                            value={newCard.name}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, name: e.target.value }))}
                            placeholder="e.g., Charizard"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="setNumber">Number in Set</Label>
                          <Input
                            id="setNumber"
                            value={newCard.setNumber}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, setNumber: e.target.value }))}
                            placeholder="e.g., 4/102"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="setName">Set Name</Label>
                          <Input
                            id="setName"
                            value={newCard.setName}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, setName: e.target.value }))}
                            placeholder="e.g., Base Set"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="condition">Condition</Label>
                          <Select
                            value={newCard.condition}
                            onValueChange={(value) => setNewCard((prev) => ({ ...prev, condition: value }))}
                          >
                            <SelectTrigger id="condition">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="NM">NM (Near Mint)</SelectItem>
                              <SelectItem value="LP">LP (Lightly Played)</SelectItem>
                              <SelectItem value="MP">MP (Moderately Played)</SelectItem>
                              <SelectItem value="HP">HP (Heavily Played)</SelectItem>
                              <SelectItem value="DMG">DMG (Damaged)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="language">Language</Label>
                          <Select
                            value={newCard.language}
                            onValueChange={(value) => setNewCard((prev) => ({ ...prev, language: value }))}
                          >
                            <SelectTrigger id="language">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="EN">English</SelectItem>
                              <SelectItem value="JP">Japanese</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="version">Version</Label>
                          <Input
                            id="version"
                            value={newCard.version}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, version: e.target.value }))}
                            placeholder="e.g., 1st Edition Holo"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="imageUrl">Image URL</Label>
                          <Input
                            id="imageUrl"
                            value={newCard.imageUrl}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, imageUrl: e.target.value }))}
                            placeholder="https://..."
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="valueUsd">Estimated Value (USD)</Label>
                          <Input
                            id="valueUsd"
                            type="number"
                            min="0"
                            step="0.01"
                            value={newCard.valueUsd}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, valueUsd: parseFloat(e.target.value) || 0 }))}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="quantity">Quantity</Label>
                          <Input
                            id="quantity"
                            type="number"
                            min="1"
                            value={newCard.quantity}
                            onChange={(e) => setNewCard((prev) => ({ ...prev, quantity: parseInt(e.target.value, 10) || 1 }))}
                          />
                        </div>
                      </div>
                      {formError && <p className="text-sm text-destructive">{formError}</p>}
                      <div className="flex justify-end gap-2 pt-4">
                        <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleAddCard} disabled={addCardMutation.isPending}>
                          {addCardMutation.isPending ? "Adding..." : "Add Card"}
                        </Button>
                      </div>
                    </TabsContent>
                    <TabsContent value="multiple" className="space-y-4 mt-4">
                      <div className="space-y-4">
                        <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                          <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                          <p className="text-sm text-muted-foreground mb-2">
                            Upload a CSV or XLS file with your card data
                          </p>
                          <Input type="file" accept=".csv,.xls,.xlsx" className="max-w-xs mx-auto" />
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Expected format: Name, Set Number, Set Name, Condition, Language, Version
                        </p>
                      </div>
                      <div className="flex justify-end gap-2 pt-4">
                        <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button disabled>Upload Cards</Button>
                      </div>
                    </TabsContent>
                  </Tabs>
                </DialogContent>
              </Dialog>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Collection Value</p>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-primary">Q{totals.gtq}</span>
                <span className="text-lg text-muted-foreground italic">${totals.usd} USD</span>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <Layers className="h-4 w-4" />
                Number of Cards
              </p>
              <p className="text-3xl font-bold">{data.cards_count}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Created
              </p>
              <p className="text-xl font-semibold">{new Date(data.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Cards in Collection</h2>
            {cards.length > 0 && (
              <span className="text-sm text-muted-foreground flex items-center gap-2">
                <Trash2 className="h-4 w-4" />
                Click the trash icon on a card to remove it
              </span>
            )}
          </div>
          <div className="space-y-3">
            {cards.length === 0 ? (
              <div className="border border-dashed rounded-lg p-10 text-center text-muted-foreground">
                No cards yet. Add your first card using the button above.
              </div>
            ) : (
              cards.map((card, index) => (
                <CardListItem
                  key={card.card_collection_id}
                  card={card}
                  formatCurrency={formatCurrency}
                  style={{ animationDelay: `${index * 0.05}s` }}
                  className="animate-slide-up"
                  onDelete={() => setCardToDelete(card.card_collection_id)}
                />
              ))
            )}
          </div>
        </div>
      </main>

      <AlertDialog open={cardToDelete !== null} onOpenChange={(open) => !open && setCardToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Card</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove this card from your collection? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteCard}>Remove</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default CollectionDetail;
