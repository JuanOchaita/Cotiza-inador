import { createContext, useContext, useState, ReactNode } from "react";

type Language = "EN" | "ES";

interface Translations {
  [key: string]: {
    EN: string;
    ES: string;
  };
}

const translations: Translations = {
  // Header
  "app.title": { EN: "PokéCollection", ES: "PokéColección" },
  "nav.addCollection": { EN: "Add Collection", ES: "Agregar Colección" },
  
  // Dashboard
  "dashboard.myCollections": { EN: "My Collections", ES: "Mis Colecciones" },
  "dashboard.collection": { EN: "Collection", ES: "Colección" },
  "dashboard.collections": { EN: "Collections", ES: "Colecciones" },
  "dashboard.noCollections": { EN: "No Collections Yet", ES: "Aún No Hay Colecciones" },
  "dashboard.noCollectionsDesc": { EN: "Start building your Pokémon card collection by creating your first collection.", ES: "Comienza a construir tu colección de cartas Pokémon creando tu primera colección." },
  "dashboard.createFirst": { EN: "Create Your First Collection", ES: "Crea Tu Primera Colección" },
  
  // Settings
  "settings.title": { EN: "Settings", ES: "Configuración" },
  "settings.account": { EN: "Account", ES: "Cuenta" },
  "settings.email": { EN: "Email Address", ES: "Correo Electrónico" },
  "settings.changePassword": { EN: "Change Password", ES: "Cambiar Contraseña" },
  "settings.language": { EN: "Language", ES: "Idioma" },
  "settings.appLanguage": { EN: "App Language", ES: "Idioma de la Aplicación" },
  "settings.selectLanguage": { EN: "Select your preferred language", ES: "Selecciona tu idioma preferido" },
  "settings.currency": { EN: "Currency", ES: "Moneda" },
  "settings.exchangeRate": { EN: "Default Exchange Rate (USD to GTQ)", ES: "Tasa de Cambio Predeterminada (USD a GTQ)" },
  "settings.exchangeRateDesc": { EN: "This will be used as the default rate for new collections", ES: "Esta será la tasa predeterminada para nuevas colecciones" },
  "settings.notifications": { EN: "Notifications", ES: "Notificaciones" },
  "settings.emailNotifications": { EN: "Email Notifications", ES: "Notificaciones por Correo" },
  "settings.emailNotificationsDesc": { EN: "Receive updates about your collections", ES: "Recibe actualizaciones sobre tus colecciones" },
  "settings.priceAlerts": { EN: "Price Alerts", ES: "Alertas de Precio" },
  "settings.priceAlertsDesc": { EN: "Get notified when card values change significantly", ES: "Recibe notificaciones cuando los valores cambien significativamente" },
  "settings.autoUpdate": { EN: "Auto-Update Prices", ES: "Actualización Automática de Precios" },
  "settings.autoUpdateDesc": { EN: "Automatically update card prices daily", ES: "Actualiza los precios automáticamente cada día" },
  "settings.privacy": { EN: "Privacy & Security", ES: "Privacidad y Seguridad" },
  "settings.exportData": { EN: "Export My Data", ES: "Exportar Mis Datos" },
  "settings.deleteAccount": { EN: "Delete Account", ES: "Eliminar Cuenta" },
  "settings.save": { EN: "Save Changes", ES: "Guardar Cambios" },
  "settings.cancel": { EN: "Cancel", ES: "Cancelar" },
  
  // Collection Detail
  "collection.backToCollections": { EN: "Back to Collections", ES: "Volver a Colecciones" },
  "collection.exchangeRate": { EN: "Exchange Rate:", ES: "Tasa de Cambio:" },
  "collection.share": { EN: "Share", ES: "Compartir" },
  "collection.addCard": { EN: "Add Card", ES: "Agregar Carta" },
  "collection.totalValue": { EN: "Total Collection Value", ES: "Valor Total de la Colección" },
  "collection.numberOfCards": { EN: "Number of Cards", ES: "Número de Cartas" },
  "collection.lastUpdated": { EN: "Last Updated", ES: "Última Actualización" },
  "collection.cardsInCollection": { EN: "Cards in Collection", ES: "Cartas en la Colección" },
  
  // Common
  "common.back": { EN: "Back", ES: "Volver" },
  
  // Navigation
  "nav.logout": { EN: "Logout", ES: "Cerrar Sesión" },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<Language>("EN");

  const t = (key: string): string => {
    return translations[key]?.[language] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};
