# AgriMitra – Farmer Market Price Assistant

A Streamlit student-project prototype based on the uploaded AgriMitra project document.

## Features
- Crop/vegetable, state, district and market selection
- Minimum, maximum and modal price display
- Market-wise modal-price comparison
- Historical price trend chart
- Gross and estimated net selling-value calculator
- Crop catalogue covering major Indian crop groups
- CSV upload for bringing in a separately verified dataset
- Source, date, unit and sample-data transparency

## Important data note
`market_prices.csv` is **illustrative sample data only**. It is not live mandi data and must not be used to make selling decisions. Replace it with a verified dataset and preserve its reporting date, price unit and source.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown in the terminal.

## CSV format for your own dataset
The application expects these columns:

`State, District, Market, Commodity, Variety, Date, Minimum Price, Maximum Price, Modal Price, Unit, Source`

Dates should be parseable by pandas. Keep the unit explicit (for example `₹/quintal` or `₹/kg`) and do not mix units in a comparison. An optional `Data Status` column can identify records as `VERIFIED`, `SAMPLE`, etc.

You can upload a CSV from the app's **Use your own market-price CSV** expander. The upload is used only during that app session; it does not overwrite the bundled CSV.

## Project files
- `app.py` – Streamlit application
- `market_prices.csv` – clearly labelled illustrative demo records
- `crop_catalog.csv` – crop and commodity catalogue
- `requirements.txt` – Python dependencies

## Crop catalogue coverage
The catalogue groups common Indian commodities into cereals and millets, pulses, oilseeds, commercial and fibre crops, vegetables, fruits, spices and condiments, plantation crops, and fodder/green-manure crops.

The list is broad but not exhaustive: India has many regional crops, local names, varieties and seasonal cultivars. Add local commodities to `crop_catalog.csv` and provide matching verified market records in `market_prices.csv`.

## Suggested GitHub upload
Create a repository named `AgriMitra-Farmer-Market-Price-Assistant`, then upload all four project files. Do not upload private API keys or personal information.
dashboard link :https://agrimitra-farmer-market-price-assistant-msheut5gcjj6a96xbzrvyz.streamlit.app/
