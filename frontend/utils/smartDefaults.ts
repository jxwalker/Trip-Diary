export type PreferencesPatch = Partial<{
  dining: {
    cuisineTypes: string[];
    dietaryRestrictions: string[];
    priceRanges: string[];
    mealPreferences: Record<string, boolean>;
  };
  interests: Record<string, Record<string, boolean>>;
  travelStyle: {
    pace: string;
    groupType: string;
    activityLevel: number;
    adventureLevel: number;
  };
}>;

export function inferDefaultsFromDestination(destination: string): PreferencesPatch {
  const d = destination.toLowerCase();
  if (d.includes("paris")) {
    return {
      dining: {
        cuisineTypes: ["Local Cuisine", "French", "Cafés"],
        dietaryRestrictions: [],
        priceRanges: ["$$", "$$$"]
      },
      interests: {
        culture: { museums: true, historicalSites: true, architecture: true, localCulture: true, theaters: true },
        lifestyle: { shopping: true, localMarkets: true, photography: true },
      } as any,
      travelStyle: { pace: "balanced", groupType: "couple", activityLevel: 3, adventureLevel: 3 },
    };
  }
  if (d.includes("tokyo")) {
    return {
      dining: {
        cuisineTypes: ["Local Cuisine", "Asian", "Seafood"],
        priceRanges: ["$", "$$", "$$$"]
      },
      interests: { lifestyle: { localMarkets: true }, culture: { museums: true } } as any,
      travelStyle: { pace: "packed", groupType: "couple", activityLevel: 4, adventureLevel: 4 },
    };
  }
  if (d.includes("bali")) {
    return {
      interests: { outdoors: { beaches: true, natureParks: true }, lifestyle: { spaWellness: true } } as any,
      travelStyle: { pace: "relaxed", groupType: "friends", activityLevel: 2, adventureLevel: 2 },
    };
  }
  // Safe default
  return {
    dining: { cuisineTypes: ["Local Cuisine"], priceRanges: ["$$"] },
    travelStyle: { pace: "balanced", groupType: "couple", activityLevel: 3, adventureLevel: 3 },
  } as any;
}

