import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar, Layers } from "lucide-react";

interface CollectionCardProps {
  collection: {
    id: number;
    name: string;
    description?: string | null;
    createdAt: string;
    cardsCount: number;
    totalValueUsd: number;
  };
  exchangeRate: number;
  formatCurrency: (usd: number) => { gtq: string; usd: string };
  onClick: () => void;
  className?: string;
  style?: React.CSSProperties;
}

const CollectionCard = ({
  collection,
  exchangeRate,
  formatCurrency,
  onClick,
  className = "",
  style,
}: CollectionCardProps) => {
  const { gtq, usd } = formatCurrency(collection.totalValueUsd);
  const formattedDate = new Date(collection.createdAt).toLocaleDateString();

  return (
    <Card
      className={`cursor-pointer transition-all duration-300 hover:shadow-card-hover hover:-translate-y-1 ${className}`}
      onClick={onClick}
      style={style}
    >
      <CardHeader>
        <CardTitle className="text-xl">{collection.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Total Value</p>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-primary">Q{gtq}</span>
            <span className="text-sm text-muted-foreground italic">${usd} USD</span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Layers className="h-4 w-4" />
            <span>{collection.cardsCount} cards</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex items-center gap-2 text-xs text-muted-foreground">
        <Calendar className="h-3 w-3" />
        <span>Created {formattedDate}</span>
      </CardFooter>
    </Card>
  );
};

export default CollectionCard;
