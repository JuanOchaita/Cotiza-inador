export interface Card {
  id: string;
  name: string;
  setNumber: string;
  setName: string;
  condition: "NM" | "LP" | "MP" | "HP" | "DMG";
  language: "EN" | "JP";
  version: string;
  valueUSD: number;
  lastUpdated: string;
  imageUrl: string;
}

export interface Collection {
  id: string;
  title: string;
  cards: Card[];
  lastUpdated: string;
}

export const sampleCollections: Collection[] = [
  {
    id: "1",
    title: "Vintage Collection",
    lastUpdated: "2025-01-15",
    cards: [
      {
        id: "c1",
        name: "Charizard",
        setNumber: "4/102",
        setName: "Base Set",
        condition: "NM",
        language: "EN",
        version: "1st Edition Holo",
        valueUSD: 2500.00,
        lastUpdated: "2025-01-15",
        imageUrl: "/placeholder.svg",
      },
      {
        id: "c2",
        name: "Blastoise",
        setNumber: "2/102",
        setName: "Base Set",
        condition: "LP",
        language: "EN",
        version: "Unlimited Holo",
        valueUSD: 350.00,
        lastUpdated: "2025-01-15",
        imageUrl: "/placeholder.svg",
      },
      {
        id: "c3",
        name: "Venusaur",
        setNumber: "15/102",
        setName: "Base Set",
        condition: "NM",
        language: "EN",
        version: "Shadowless Holo",
        valueUSD: 800.00,
        lastUpdated: "2025-01-15",
        imageUrl: "/placeholder.svg",
      },
    ],
  },
  {
    id: "2",
    title: "Japanese Exclusives",
    lastUpdated: "2025-01-10",
    cards: [
      {
        id: "c4",
        name: "Pikachu",
        setNumber: "25/25",
        setName: "25th Anniversary",
        condition: "NM",
        language: "JP",
        version: "Gold Star",
        valueUSD: 450.00,
        lastUpdated: "2025-01-10",
        imageUrl: "/placeholder.svg",
      },
      {
        id: "c5",
        name: "Mew",
        setNumber: "11/110",
        setName: "Legendary Collection",
        condition: "MP",
        language: "JP",
        version: "Holo",
        valueUSD: 180.00,
        lastUpdated: "2025-01-10",
        imageUrl: "/placeholder.svg",
      },
    ],
  },
  {
    id: "3",
    title: "Modern Hits",
    lastUpdated: "2025-01-12",
    cards: [
      {
        id: "c6",
        name: "Umbreon VMAX",
        setNumber: "215/203",
        setName: "Evolving Skies",
        condition: "NM",
        language: "EN",
        version: "Alternate Art",
        valueUSD: 320.00,
        lastUpdated: "2025-01-12",
        imageUrl: "/placeholder.svg",
      },
      {
        id: "c7",
        name: "Rayquaza VMAX",
        setNumber: "218/203",
        setName: "Evolving Skies",
        condition: "NM",
        language: "EN",
        version: "Alternate Art",
        valueUSD: 280.00,
        lastUpdated: "2025-01-12",
        imageUrl: "/placeholder.svg",
      },
      {
        id: "c8",
        name: "Pikachu VMAX",
        setNumber: "188/185",
        setName: "Vivid Voltage",
        condition: "LP",
        language: "EN",
        version: "Rainbow Rare",
        valueUSD: 150.00,
        lastUpdated: "2025-01-12",
        imageUrl: "/placeholder.svg",
      },
    ],
  },
];
