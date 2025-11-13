import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Calendar, Layers, Plus, Upload, Share2, Download, Link2, Check, Loader2 } from "lucide-react";
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
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { useAuth } from "@/contexts/AuthContext";
import { 
  getCollection, 
  getCardsByCollection, 
  updateCollectionExchangeRate,
  addCardToCollection,
  removeCardFromCollection,
  Collection,
  Card 
} from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const CollectionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [collection, setCollection] = useState<Collection | null>(null);
  const [cards, setCards] = useState<Card[]>([]);
  const [exchangeRate, setExchangeRate] = useState(7.75);
  const [loading, setLoading] = useState(true);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [cardToDelete, setCardToDelete] = useState<number | null>(null);
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [urlCopied, setUrlCopied] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state for single card
  const [newCard, setNewCard] = useState({
    name: "",
    setNumber: "",
    setName: "",
    condition: 1, // condition_id
    language: 1, // language_id
    version: "",
    quantity: 1,
  });

  useEffect(() => {
    if (!user || !id) {
      navigate("/");
      return;
    }

    const fetchData = async () => {
      try {
        const [collectionData, cardsData] = await Promise.all([
          getCollection(Number(id)),
          getCardsByCollection(Number(id))
        ]);
        
        setCollection(collectionData);
        setCards(cardsData);
        setExchangeRate(collectionData.exchange_rate);
      } catch (error) {
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to fetch collection",
          variant: "destructive",
        });
        navigate("/dashboard");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, user, navigate, toast]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!collection) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Collection Not Found</h2>
          <Button onClick={() => navigate("/dashboard")}>Back to Dashboard</Button>
        </div>
      </div>
    );
  }

  const handleAddCard = async () => {
    if (!collection) return;
    
    setSubmitting(true);
    try {
      await addCardToCollection({
        collection_id: collection.collection_id,
        condition_id: newCard.condition,
        quantity: newCard.quantity,
        card_name: newCard.name,
        number_in_set: newCard.setNumber,
        set_name: newCard.setName,
        language_id: newCard.language,
        edition: newCard.version,
      });

      // Refresh cards
      const updatedCards = await getCardsByCollection(collection.collection_id);
      setCards(updatedCards);

      toast({
        title: "Success",
        description: "Card added successfully",
      });

      setNewCard({
        name: "",
        setNumber: "",
        setName: "",
        condition: 1,
        language: 1,
        version: "",
        quantity: 1,
      });
      setIsAddDialogOpen(false);
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add card",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteCard = async (cardId: number) => {
    if (!collection) return;
    
    try {
      await removeCardFromCollection(cardId, collection.collection_id);
      setCards(cards.filter(c => c.card_id !== cardId));
      toast({
        title: "Success",
        description: "Card removed successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to remove card",
        variant: "destructive",
      });
    }
    setCardToDelete(null);
  };

  const handleExchangeRateChange = async (newRate: string) => {
    if (!collection) return;
    
    const rate = parseFloat(newRate);
    setExchangeRate(rate);
    
    try {
      await updateCollectionExchangeRate(collection.collection_id, {
        new_exchange_rate: rate
      });
      toast({
        title: "Success",
        description: "Exchange rate updated",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update exchange rate",
        variant: "destructive",
      });
    }
  };

  const formatCurrency = (usd: number) => {
    const gtq = usd * exchangeRate;
    return {
      gtq: formatNumber(gtq),
      usd: formatNumber(usd),
    };
  };

  const handleDownloadPDF = () => {
    if (!collection) return;
    
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text(collection.title, 14, 20);
    
    // Add collection info
    doc.setFontSize(12);
    const totalValue = collection.collection_price_usd;
    const { gtq, usd } = formatCurrency(totalValue);
    doc.text(`Total Value: Q${gtq} (USD $${usd})`, 14, 30);
    doc.text(`Number of Cards: ${totalCards}`, 14, 37);
    doc.text(`Last Updated: ${new Date(collection.created_at).toLocaleDateString()}`, 14, 44);
    
    // Add cards table
    const tableData = cards.map(card => {
      return [
        card.name,
        card.set_number,
        card.set_name,
        card.condition,
        card.language,
        card.version,
        card.quantity.toString(),
      ];
    });
    
    autoTable(doc, {
      head: [['Name', 'Set #', 'Set Name', 'Condition', 'Lang', 'Version', 'Qty']],
      body: tableData,
      startY: 50,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [59, 130, 246] },
    });
    
    doc.save(`${collection.title}.pdf`);
    setIsShareOpen(false);
  };

  const handleCopyURL = () => {
    const url = `https://myapp.com/collections/${id}`;
    navigator.clipboard.writeText(url);
    setUrlCopied(true);
    setTimeout(() => setUrlCopied(false), 2000);
  };

  const totalValue = collection.collection_price_usd;
  const totalCards = cards.reduce((sum, card) => sum + card.quantity, 0);
  const { gtq, usd } = formatCurrency(totalValue);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <Button
              variant="ghost"
              onClick={() => navigate("/dashboard")}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Collections
            </Button>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium">Exchange Rate:</label>
              <Select
                value={exchangeRate.toString()}
                onValueChange={handleExchangeRateChange}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 11 }, (_, i) => (7.0 + i * 0.1).toFixed(1)).map(
                    (rate) => (
                      <SelectItem key={rate} value={rate}>
                        {rate}
                      </SelectItem>
                    )
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="bg-gradient-card rounded-lg p-6 shadow-card mb-8 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold">{collection.title}</h1>
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
                    <Button
                      variant="outline"
                      className="w-full justify-start gap-2"
                      onClick={handleDownloadPDF}
                    >
                      <Download className="h-4 w-4" />
                      Download PDF
                    </Button>
                    <div className="space-y-2">
                      <div className="flex gap-2">
                        <Input
                          readOnly
                          value={`https://myapp.com/collections/${id}`}
                          className="text-xs"
                        />
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={handleCopyURL}
                        >
                          {urlCopied ? (
                            <Check className="h-4 w-4 text-green-500" />
                          ) : (
                            <Link2 className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Get shareable URL
                      </p>
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
                  <DialogDescription>
                    Add a single card or upload multiple cards via file.
                  </DialogDescription>
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
                          onChange={(e) => setNewCard({ ...newCard, name: e.target.value })}
                          placeholder="e.g., Charizard"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="setNumber">Number in Set</Label>
                        <Input
                          id="setNumber"
                          value={newCard.setNumber}
                          onChange={(e) => setNewCard({ ...newCard, setNumber: e.target.value })}
                          placeholder="e.g., 4/102"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="setName">Set Name</Label>
                        <Input
                          id="setName"
                          value={newCard.setName}
                          onChange={(e) => setNewCard({ ...newCard, setName: e.target.value })}
                          placeholder="e.g., Base Set"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="condition">Condition</Label>
                        <Select
                          value={String(newCard.condition)}
                          onValueChange={(value) => setNewCard({ ...newCard, condition: parseInt(value) })}
                        >
                          <SelectTrigger id="condition">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">NM (Near Mint)</SelectItem>
                            <SelectItem value="2">LP (Lightly Played)</SelectItem>
                            <SelectItem value="3">MP (Moderately Played)</SelectItem>
                            <SelectItem value="4">HP (Heavily Played)</SelectItem>
                            <SelectItem value="5">DMG (Damaged)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="language">Language</Label>
                        <Select
                          value={String(newCard.language)}
                          onValueChange={(value) => setNewCard({ ...newCard, language: parseInt(value) })}
                        >
                          <SelectTrigger id="language">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">English</SelectItem>
                            <SelectItem value="2">Japanese</SelectItem>
                            <SelectItem value="3">Spanish</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="version">Version</Label>
                        <Input
                          id="version"
                          value={newCard.version}
                          onChange={(e) => setNewCard({ ...newCard, version: e.target.value })}
                          placeholder="e.g., 1st Edition Holo"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="quantity">Quantity</Label>
                        <Input
                          id="quantity"
                          type="number"
                          min="1"
                          value={newCard.quantity}
                          onChange={(e) => setNewCard({ ...newCard, quantity: parseInt(e.target.value) || 1 })}
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 pt-4">
                      <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleAddCard} disabled={!newCard.name || !newCard.setName || submitting}>
                        {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Add Card
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
                <span className="text-3xl font-bold text-primary">Q{gtq}</span>
                <span className="text-lg text-muted-foreground italic">${usd} USD</span>
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <Layers className="h-4 w-4" />
                Number of Cards
              </p>
              <p className="text-3xl font-bold">{totalCards}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Last Updated
              </p>
              <p className="text-xl font-semibold">{new Date(collection.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Cards in Collection</h2>
          <div className="space-y-3">
            {cards.map((card, index) => (
              <CardListItem
                key={card.card_id}
                card={card}
                formatCurrency={formatCurrency}
                style={{ animationDelay: `${index * 0.05}s` }}
                className="animate-slide-up"
                onDelete={() => setCardToDelete(card.card_id)}
              />
            ))}
          </div>
        </div>
      </main>

      <AlertDialog open={!!cardToDelete} onOpenChange={() => setCardToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Card</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove this card from your collection? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => cardToDelete && handleDeleteCard(cardToDelete)}>
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default CollectionDetail;
