import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import CollectionDetail from "./pages/CollectionDetail";
import AddCollection from "./pages/AddCollection";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import PrivateRoute from "@/components/PrivateRoute";

const App = () => (
  <TooltipProvider>
    <Toaster />
    <Sonner />
    <Routes>
      <Route path="/" element={<Login />} />
      <Route
        path="/dashboard"
        element={(
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        )}
      />
      <Route
        path="/collection/:id"
        element={(
          <PrivateRoute>
            <CollectionDetail />
          </PrivateRoute>
        )}
      />
      <Route
        path="/add-collection"
        element={(
          <PrivateRoute>
            <AddCollection />
          </PrivateRoute>
        )}
      />
      <Route
        path="/settings"
        element={(
          <PrivateRoute>
            <Settings />
          </PrivateRoute>
        )}
      />
      {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  </TooltipProvider>
);

export default App;
