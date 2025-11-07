import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest, ApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

const AddCollection = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () =>
      apiRequest("/collections", {
        method: "POST",
        token,
        body: {
          name: formData.name,
          description: formData.description || null,
        },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["collections"] });
      navigate("/dashboard");
    },
    onError: (err: unknown) => {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Error creating collection.");
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    mutation.mutate();
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
              Add New Collection
            </h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <form onSubmit={handleSubmit} className="space-y-6 animate-fade-in">
          <div className="bg-card rounded-lg border p-6 space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Collection Name</Label>
              <Input
                id="name"
                placeholder="e.g., Base Set Collection"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                placeholder="Add notes about this collection..."
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                rows={4}
              />
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}

            <div className="flex gap-3 pt-4">
              <Button type="submit" className="flex-1" disabled={mutation.isPending}>
                {mutation.isPending ? "Creating..." : "Create Collection"}
              </Button>
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={() => navigate("/dashboard")}
              >
                Cancel
              </Button>
            </div>
          </div>

          <div className="bg-muted/50 rounded-lg border border-dashed p-6">
            <h3 className="font-semibold mb-3">What's Next?</h3>
            <p className="text-sm text-muted-foreground">
              After creating your collection, you'll be able to add individual
              Pokémon cards, track their values, and manage their conditions.
            </p>
          </div>
        </form>
      </main>
    </div>
  );
};

export default AddCollection;
