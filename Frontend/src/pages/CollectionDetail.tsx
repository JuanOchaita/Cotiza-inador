import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Calendar, Layers, Plus, Upload, Share2, Download, Link2, Check } from "lucide-react";
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
import { sampleCollections } from "@/data/sampleData";
import CardListItem from "@/components/CardListItem";
import { formatNumber } from "@/lib/utils";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

const CollectionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [exchangeRate, setExchangeRate] = useState(7.75);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [cardToDelete, setCardToDelete] = useState<string | null>(null);
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [urlCopied, setUrlCopied] = useState(false);
  
  const collection = sampleCollections.find((c) => c.id === id);
  const [cards, setCards] = useState(collection?.cards || []);

  // Form state for single card
  const [newCard, setNewCard] = useState({
    name: "",
    setNumber: "",
    setName: "",
    condition: "NM" as const,
    language: "EN" as const,
    version: "",
  });

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

  const handleAddCard = () => {
    const card = {
      id: `c${Date.now()}`,
      name: newCard.name,
      setNumber: newCard.setNumber,
      setName: newCard.setName,
      condition: newCard.condition,
      language: newCard.language,
      version: newCard.version,
      valueUSD: 0,
      lastUpdated: new Date().toISOString().split('T')[0],
      imageUrl: "/placeholder.svg",
    };
    setCards([...cards, card]);
    setNewCard({
      name: "",
      setNumber: "",
      setName: "",
      condition: "NM",
      language: "EN",
      version: "",
    });
    setIsAddDialogOpen(false);
  };

  const handleDeleteCard = (cardId: string) => {
    setCards(cards.filter(c => c.id !== cardId));
    setCardToDelete(null);
  };

  const formatCurrency = (usd: number) => {
    const gtq = usd * exchangeRate;
    return {
      gtq: formatNumber(gtq),
      usd: formatNumber(usd),
    };
  };

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text(collection.title, 14, 20);
    
    // Add collection info
    doc.setFontSize(12);
    doc.text(`Total Value: Q${gtq} (USD $${usd})`, 14, 30);
    doc.text(`Number of Cards: ${cards.length}`, 14, 37);
    doc.text(`Last Updated: ${collection.lastUpdated}`, 14, 44);
    
    // Add cards table
    const tableData = cards.map(card => {
      const { gtq, usd } = formatCurrency(card.valueUSD);
      return [
        card.name,
        card.setNumber,
        card.setName,
        card.condition,
        card.language,
        card.version,
        `Q${gtq}`,
        `$${usd}`,
      ];
    });
    
    autoTable(doc, {
      head: [['Name', 'Set #', 'Set Name', 'Condition', 'Lang', 'Version', 'GTQ', 'USD']],
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

  const totalValue = cards.reduce((sum, card) => sum + card.valueUSD, 0);
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
                onValueChange={(value) => setExchangeRate(parseFloat(value))}
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
                          value={newCard.condition}
                          onValueChange={(value: any) => setNewCard({ ...newCard, condition: value })}
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
                          onValueChange={(value: any) => setNewCard({ ...newCard, language: value })}
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
                          onChange={(e) => setNewCard({ ...newCard, version: e.target.value })}
                          placeholder="e.g., 1st Edition Holo"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2 pt-4">
                      <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleAddCard} disabled={!newCard.name || !newCard.setName}>
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
              <p className="text-3xl font-bold">{cards.length}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Last Updated
              </p>
              <p className="text-xl font-semibold">{collection.lastUpdated}</p>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Cards in Collection</h2>
          <div className="space-y-3">
            {cards.map((card, index) => (
              <CardListItem
                key={card.id}
                card={card}
                formatCurrency={formatCurrency}
                style={{ animationDelay: `${index * 0.05}s` }}
                className="animate-slide-up"
                onDelete={() => setCardToDelete(card.id)}
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
