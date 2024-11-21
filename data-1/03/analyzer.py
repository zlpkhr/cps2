import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from typing import Optional

class GeoNamesAnalyzer:
    def __init__(self, country_code: str):
        """
        Initialize the analyzer for a specific country.
        Args:
            country_code: Two-letter country code (e.g., 'FR' for France, 'US' for United States)
        """
        self.country_code = country_code
        
        # Load necessary GeoNames dumps with proper settings
        self.places_df = pd.read_csv(f'{country_code}/{country_code}.txt', sep='\t', header=None,
                                   names=['geonameid', 'name', 'asciiname', 'alternatenames',
                                         'latitude', 'longitude', 'feature_class', 'feature_code',
                                         'country_code', 'cc2', 'admin1_code', 'admin2_code',
                                         'admin3_code', 'admin4_code', 'population', 'elevation',
                                         'dem', 'timezone', 'modification_date'],
                                   low_memory=False,
                                   dtype={'admin1_code': str, 'admin2_code': str})
        
        # Load admin codes and FIPS codes
        self.admin1_df = pd.read_csv('admin1CodesASCII.txt', sep='\t', header=None,
                                   names=['code', 'name', 'name_ascii', 'geonameid'])
        self.admin2_df = pd.read_csv('admin2Codes.txt', sep='\t', header=None,
                                   names=['code', 'name', 'name_ascii', 'geonameid'])

        # If US, also load FIPS codes mappings
        if country_code == 'US':
            # In real implementation, we would load FIPS codes from GeoNames' special files
            # For US locations, admin2_code is actually the county FIPS code
            self.fips_df = pd.read_csv('US_FIPS_codes.txt', sep='\t', 
                                     dtype={'fips': str, 'state': str, 'county': str})

    def get_fips_info(self, admin1_code: str, admin2_code: str) -> Optional[dict]:
        """Get FIPS code information for a location."""
        if self.country_code == 'US':
            # For US locations, construct FIPS info
            fips_code = f"{admin1_code}{admin2_code}"
            try:
                fips_info = self.fips_df[self.fips_df['fips'] == fips_code].iloc[0]
                return {
                    'fips_code': fips_code,
                    'fips_name': f"{fips_info['county']}, {fips_info['state']}"
                }
            except (IndexError, KeyError):
                return None
        else:
            # For non-US locations, FIPS codes are not applicable
            return None

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate the great circle distance between two points on Earth."""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def find_location_info(self, place_name):
        # Find the target location
        target_place = self.places_df[self.places_df['name'] == place_name].iloc[0]
        target_lat, target_lon = target_place['latitude'], target_place['longitude']

        # Get FIPS code information if applicable
        fips_info = self.get_fips_info(target_place['admin1_code'], 
                                     target_place['admin2_code'])

        # Get admin codes based on country
        admin1_code = f"{self.country_code}.{target_place['admin1_code']}"
        admin2_code = f"{self.country_code}.{target_place['admin1_code']}.{target_place['admin2_code']}"
        
        # Get admin division info
        admin2_info = self.admin2_df[self.admin2_df['code'] == admin2_code].iloc[0]

        # Find the closest airport
        airports = self.places_df[self.places_df['feature_code'].isin(['AIRP', 'AIRF'])].copy()
        airports.loc[:, 'distance'] = airports.apply(
            lambda x: self.haversine_distance(target_lat, target_lon, 
                                            x['latitude'], x['longitude']), axis=1)
        closest_airport = airports.nsmallest(1, 'distance').iloc[0]

        # Calculate division population
        admin2_population = self.places_df[
            (self.places_df['admin1_code'] == target_place['admin1_code']) &
            (self.places_df['admin2_code'] == target_place['admin2_code'])
        ]['population'].sum()

        # Find closest populated places
        populated_places = self.places_df[
            (self.places_df['feature_class'] == 'P') &
            (self.places_df['name'] != place_name) &
            (self.places_df['population'] > 0)
        ].copy()
        
        populated_places.loc[:, 'distance'] = populated_places.apply(
            lambda x: self.haversine_distance(target_lat, target_lon, 
                                            x['latitude'], x['longitude']), axis=1)
        closest_places = populated_places.nsmallest(5, 'distance')

        return {
            'target_place': place_name,
            'closest_airport': {
                'name': closest_airport['name'],
                'distance_km': round(closest_airport['distance'], 2)
            },
            'admin_info': {
                'admin2_name': admin2_info['name'],
                'fips_info': fips_info,  # Will be None for non-US locations
                'admin2_population': int(admin2_population)
            },
            'closest_places': [
                {
                    'name': row['name'],
                    'distance_km': round(row['distance'], 2),
                    'population': int(row['population'])
                }
                for _, row in closest_places.iterrows()
            ]
        }

def main():
    # Example for France
    analyzer_fr = GeoNamesAnalyzer('FR')
    result_fr = analyzer_fr.find_location_info("Gare de Saint-Étienne-Châteaucreux")
    
    print(f"\nAnalysis for {result_fr['target_place']}:")
    print("\n1. Closest Airport:")
    print(f"   {result_fr['closest_airport']['name']} ({result_fr['closest_airport']['distance_km']} km)")
    
    print("\n2. Administrative Division Info:")
    print(f"   Second Administrative Division: {result_fr['admin_info']['admin2_name']}")
    if result_fr['admin_info']['fips_info']:
        print(f"   FIPS Code: {result_fr['admin_info']['fips_info']['fips_code']}")
        print(f"   FIPS Name: {result_fr['admin_info']['fips_info']['fips_name']}")
    else:
        print("   (FIPS codes not applicable for France)")
    print(f"   Total Population: {result_fr['admin_info']['admin2_population']:,}")
    
    print("\n3. Five Closest Populated Places:")
    for i, place in enumerate(result_fr['closest_places'], 1):
        print(f"   {i}. {place['name']} - {place['distance_km']} km (pop: {place['population']:,})")

if __name__ == "__main__":
    main()