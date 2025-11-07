import { Card, CardContent } from "@/components/ui/card";
import { Calendar, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatNumber } from "@/lib/utils";

interface CardListItemProps {
  card: {
    card_collection_id: number;
    name: string;
    set_number: string | null;
    set_name: string | null;
    condition: string;
    language: string;
    version: string | null;
    value_usd: number;
    quantity: number;
    image_url: string | null;
  };
  formatCurrency: (usd: number) => { gtq: string; usd: string };
  className?: string;
  style?: React.CSSProperties;
  onDelete?: () => void;
}

const CardListItem = ({ card, formatCurrency, className = "", style, onDelete }: CardListItemProps) => {
  const { gtq, usd } = formatCurrency(card.value_usd ?? 0);

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case "NM":
        return "bg-green-100 text-green-800 border-green-200";
      case "LP":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "MP":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "HP":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "DMG":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <Card className={`hover:shadow-card-hover transition-all duration-300 ${className}`} style={style}>
      <CardContent className="p-4">
        <div className="flex gap-4">
          <div className="flex-shrink-0">
            <img
              src={card.image_url ?? "/placeholder.svg"}
              alt={card.name}
              className="w-24 h-32 object-cover rounded-lg shadow-sm"
            />
          </div>
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div>
                <h3 className="text-lg font-bold text-foreground">{card.name}</h3>
                {(card.set_number || card.set_name) && (
                  <p className="text-sm text-muted-foreground">
                    {card.set_number ?? "-"} • {card.set_name ?? "Unknown"}
                  </p>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge className={getConditionColor(card.condition)} variant="outline">
                  {card.condition}
                </Badge>
                <Badge variant="outline">{card.language}</Badge>
                {card.version && <Badge variant="secondary">{card.version}</Badge>}
                <Badge variant="secondary">Qty: {card.quantity}</Badge>
              </div>
            </div>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Card Value</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold text-primary">Q{gtq}</span>
                  <span className="text-sm text-muted-foreground italic">${usd} USD</span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span>Total per card: ${formatNumber(card.value_usd ?? 0)}</span>
              </div>
            </div>
          </div>
          {onDelete && (
            <div className="flex-shrink-0">
              <Button
                variant="ghost"
                size="icon"
                onClick={onDelete}
                className="text-destructive hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="h-5 w-5" />
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default CardListItem;
