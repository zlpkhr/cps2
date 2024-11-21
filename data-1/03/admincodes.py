from collections import defaultdict
import re
import csv

codes = { 'AF':'Afghanistan',
 'AL':'Albania',
 'DZ':'Algeria',
 'AS':'American Samoa',
 'AD':'Andorra',
 'AO':'Angola',
 'AI':'Anguilla',
 'AQ':'Antarctica',
 'AG':'Antigua and Barbuda',
 'AR':'Argentina',
 'AM':'Armenia',
 'AW':'Aruba',
 'AU':'Australia',
 'AT':'Austria',
 'AZ':'Azerbaijan',
 'BS':'Bahamas',
 'BH':'Bahrain',
 'BD':'Bangladesh',
 'BB':'Barbados',
 'BY':'Belarus',
 'BE':'Belgium',
 'BZ':'Belize',
 'BJ':'Benin',
 'BM':'Bermuda',
 'BT':'Bhutan',
 'BO':'Bolivia Plurinational State of',
 'BQ':'Bonaire Sint Eustatius and Saba',
 'BA':'Bosnia and Herzegovina',
 'BW':'Botswana',
 'BV':'Bouvet Island',
 'BR':'Brazil',
 'IO':'British Indian Ocean Territory',
 'BN':'Brunei Darussalam',
 'BG':'Bulgaria',
 'BF':'Burkina Faso',
 'BI':'Burundi',
 'KH':'Cambodia',
 'CM':'Cameroon',
 'CA':'Canada',
 'CV':'Cape Verde',
 'KY':'Cayman Islands',
 'CF':'Central African Republic',
 'TD':'Chad',
 'CL':'Chile',
 'CN':'China',
 'CX':'Christmas Island',
 'CC':'Cocos (Keeling) Islands',
 'CO':'Colombia',
 'KM':'Comoros',
 'CG':'Congo',
 'CD':'Congo the Democratic Republic of the',
 'CK':'Cook Islands',
 'CR':'Costa Rica',
 'HR':'Croatia',
 'CU':'Cuba',
 'CW':'Curaçao',
 'CY':'Cyprus',
 'CZ':'Czech Republic',
 'CI':"Côte d'Ivoire",
 'DK':'Denmark',
 'DJ':'Djibouti',
 'DM':'Dominica',
 'DO':'Dominican Republic',
 'EC':'Ecuador',
 'EG':'Egypt',
 'SV':'El Salvador',
 'GQ':'Equatorial Guinea',
 'ER':'Eritrea',
 'EE':'Estonia',
 'ET':'Ethiopia',
 'FK':'Falkland Islands (Malvinas)',
 'FO':'Faroe Islands',
 'FJ':'Fiji',
 'FI':'Finland',
 'FR':'France',
 'GF':'French Guiana',
 'PF':'French Polynesia',
 'TF':'French Southern Territories',
 'GA':'Gabon',
 'GM':'Gambia',
 'GE':'Georgia',
 'DE':'Germany',
 'GH':'Ghana',
 'GI':'Gibraltar',
 'GR':'Greece',
 'GL':'Greenland',
 'GD':'Grenada',
 'GP':'Guadeloupe',
 'GU':'Guam',
 'GT':'Guatemala',
 'GG':'Guernsey',
 'GN':'Guinea',
 'GW':'Guinea-Bissau',
 'GY':'Guyana',
 'HT':'Haiti',
 'HM':'Heard Island and McDonald Islands',
 'VA':'Holy See (Vatican City State)',
 'HN':'Honduras',
 'HK':'Hong Kong',
 'HU':'Hungary',
 'IS':'Iceland',
 'IN':'India',
 'ID':'Indonesia',
 'IR':'Iran Islamic Republic of',
 'IQ':'Iraq',
 'IE':'Ireland',
 'IM':'Isle of Man',
 'IL':'Israel',
 'IT':'Italy',
 'JM':'Jamaica',
 'JP':'Japan',
 'JE':'Jersey',
 'JO':'Jordan',
 'KZ':'Kazakhstan',
 'KE':'Kenya',
 'KI':'Kiribati',
 'KP':"Korea Democratic People's Republic of",
 'KR':'Korea Republic of',
 'KW':'Kuwait',
 'KG':'Kyrgyzstan',
 'LA':"Lao People's Democratic Republic",
 'LV':'Latvia',
 'LB':'Lebanon',
 'LS':'Lesotho',
 'LR':'Liberia',
 'LY':'Libya',
 'LI':'Liechtenstein',
 'LT':'Lithuania',
 'LU':'Luxembourg',
 'MO':'Macao',
 'MK':'Macedonia the former Yugoslav Republic of',
 'MG':'Madagascar',
 'MW':'Malawi',
 'MY':'Malaysia',
 'MV':'Maldives',
 'ML':'Mali',
 'MT':'Malta',
 'MH':'Marshall Islands',
 'MQ':'Martinique',
 'MR':'Mauritania',
 'MU':'Mauritius',
 'YT':'Mayotte',
 'MX':'Mexico',
 'FM':'Micronesia Federated States of',
 'MD':'Moldova Republic of',
 'MC':'Monaco',
 'MN':'Mongolia',
 'ME':'Montenegro',
 'MS':'Montserrat',
 'MA':'Morocco',
 'MZ':'Mozambique',
 'MM':'Myanmar',
 'NA':'Namibia',
 'NR':'Nauru',
 'NP':'Nepal',
 'NL':'Netherlands',
 'NC':'New Caledonia',
 'NZ':'New Zealand',
 'NI':'Nicaragua',
 'NE':'Niger',
 'NG':'Nigeria',
 'NU':'Niue',
 'NF':'Norfolk Island',
 'MP':'Northern Mariana Islands',
 'NO':'Norway',
 'OM':'Oman',
 'PK':'Pakistan',
 'PW':'Palau',
 'PS':'Palestine State of',
 'PA':'Panama',
 'PG':'Papua New Guinea',
 'PY':'Paraguay',
 'PE':'Peru',
 'PH':'Philippines',
 'PN':'Pitcairn',
 'PL':'Poland',
 'PT':'Portugal',
 'PR':'Puerto Rico',
 'QA':'Qatar',
 'RO':'Romania',
 'RU':'Russian Federation',
 'RW':'Rwanda',
 'RE':'Réunion',
 'BL':'Saint Barthélemy',
 'SH':'Saint Helena Ascension and Tristan da Cunha',
 'KN':'Saint Kitts and Nevis',
 'LC':'Saint Lucia',
 'MF':'Saint Martin (French part)',
 'PM':'Saint Pierre and Miquelon',
 'VC':'Saint Vincent and the Grenadines',
 'WS':'Samoa',
 'SM':'San Marino',
 'ST':'Sao Tome and Principe',
 'SA':'Saudi Arabia',
 'SN':'Senegal',
 'RS':'Serbia',
 'SC':'Seychelles',
 'SL':'Sierra Leone',
 'SG':'Singapore',
 'SX':'Sint Maarten (Dutch part)',
 'SK':'Slovakia',
 'SI':'Slovenia',
 'SB':'Solomon Islands',
 'SO':'Somalia',
 'ZA':'South Africa',
 'GS':'South Georgia and the South Sandwich Islands',
 'SS':'South Sudan',
 'ES':'Spain',
 'LK':'Sri Lanka',
 'SD':'Sudan',
 'SR':'Suriname',
 'SJ':'Svalbard and Jan Mayen',
 'SZ':'Swaziland',
 'SE':'Sweden',
 'CH':'Switzerland',
 'SY':'Syrian Arab Republic',
 'TW':'Taiwan Province of China',
 'TJ':'Tajikistan',
 'TZ':'Tanzania United Republic of',
 'TH':'Thailand',
 'TL':'Timor-Leste',
 'TG':'Togo',
 'TK':'Tokelau',
 'TO':'Tonga',
 'TT':'Trinidad and Tobago',
 'TN':'Tunisia',
 'TR':'Turkey',
 'TM':'Turkmenistan',
 'TC':'Turks and Caicos Islands',
 'TV':'Tuvalu',
 'UG':'Uganda',
 'UA':'Ukraine',
 'AE':'United Arab Emirates',
 'GB':'United Kingdom',
 'US':'United States',
 'UM':'United States Minor Outlying Islands',
 'UY':'Uruguay',
 'UZ':'Uzbekistan',
 'VU':'Vanuatu',
 'VE':'Venezuela Bolivarian Republic of',
 'VN':'Viet Nam',
 'VG':'Virgin Islands British',
 'VI':'Virgin Islands U.S.',
 'WF':'Wallis and Futuna',
 'EH':'Western Sahara',
 'YE':'Yemen',
 'ZM':'Zambia',
 'ZW':'Zimbabwe',
 'AX':'Åland Islands'}

def analyze_admin_regions(input_file):
    """
    Analyze admin regions from input file and return results
    """
    # Dictionary to count regions per country
    country_counts = defaultdict(int)
    
    # Regular expression to match the pattern COUNTRYCODE.[WHATEVER]
    pattern = r'([A-Z]{2})\.\d+'
    
    try:
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                match = re.match(pattern, line)
                if match:
                    country_code = match.group(1)
                    # Increment count for this country
                    country_counts[country_code] += 1

        # Create list of results
        results = []
        for country_code in sorted(country_counts.keys()):
            results.append({
                'country_code': country_code,
                'country_name': codes.get(country_code, 'Unknown'),
                'admin1_count': country_counts[country_code]
            })
        
        return results
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        return []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []

def write_csv(results, output_file='admin_regions_count.csv'):
    """Write results to CSV file"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['country_code', 'country_name', 'admin1_count'])
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully wrote results to {output_file}")
    except Exception as e:
        print(f"Error writing CSV file: {str(e)}")

def main():
    input_file = 'admin1CodesASCII.txt'
    output_file = 'admin_regions_count.csv'
    
    # Process the data
    results = analyze_admin_regions(input_file)
    
    if results:
        # Write results to CSV
        write_csv(results, output_file)
        
        # Print summary
        print("\nSummary of results:")
        print(f"Processed {sum(r['admin1_count'] for r in results)} total admin1 regions")
        print(f"Found data for {len(results)} countries")
        
        # Print first few results as sample
        print("\nFirst few results:")
        for result in results[:5]:
            print(f"{result['country_code']},{result['country_name']},{result['admin1_count']}")

if __name__ == "__main__":
    main()