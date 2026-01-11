# Earthquake Exposure Analysis

A project to figure out which cities in Asia are most at risk from earthquakes.

## What it does

This project:
1. Downloads earthquake data from USGS (all M5.0+ earthquakes in 2025)
2. Calculates Peak Ground Acceleration (PGA) for major Asian cities
3. Makes interactive maps and charts to show the results

## How to run it

### 1. Clone the repo

First, fork this repository on GitHub, then clone it:
```bash
git clone https://github.com/YOUR_USERNAME/earthquake_exposure.git
cd earthquake_exposure
```

### 2. Install dependencies

Make sure you have Python 3.10+ and Poetry installed, then:
```bash
poetry install
```

### 3. Run the analysis

Open the Jupyter notebook:
```bash
poetry run jupyter notebook notebooks/exploration.ipynb
```


Then just run all the cells. It will:
- Fetch the earthquake data
- Calculate risk for each city
- Generate the visualizations

### Output files

Results are saved to the `outputs/` folder:
- `seismic_risk_results.csv` - all the city risk data
- `summary_statistics.txt` - quick overview of results
- `interactive_risk_map.html` - the interactive map

### 4. Run the REST API (optional)

We also made a simple API to get earthquake data:
```bash
poetry run uvicorn earthquake_exposure.api:app --reload
```

Then go to http://localhost:8000/docs to see the API documentation.

**Available endpoints:**
- `http://localhost:8000/` - Welcome message
- `http://localhost:8000/latest_quakes` - Get recent M5+ earthquakes
- `http://localhost:8000/docs` - Interactive API docs

### 5. Run the tests

To run the tests:
```bash
poetry run python tests/verify_pga_pipeline.py
```

This runs 5 tests to check that everything works.

### 6. Alternative: Using Conda

If you prefer using Conda instead of Poetry, you can create an environment manually:

```bash
conda create -n earthquake python=3.10 geopandas pandas numpy scipy plotly requests fastapi uvicorn -y
conda activate earthquake
```

Then you can run the commands directly:
- Notebook: `jupyter notebook notebooks/exploration.ipynb`
- API: `cd src && python -m uvicorn earthquake_exposure.api:app --reload`
- Tests: `python tests/verify_pga_pipeline.py`

## Project structure

```
earthquake_exposure/
├── src/earthquake_exposure/
│   ├── acquire.py        # gets the data
│   ├── preprocess.py     # cleans it up
│   ├── spatial_index.py  # KD-tree for fast searching
│   ├── metrics.py        # PGA calculations
│   └── viz.py            # makes the maps
├── notebooks/
│   └── exploration.ipynb # main analysis
├── outputs/              # all results go here
│   ├── interactive_risk_map.html
│   ├── seismic_risk_results.csv
│   └── summary_statistics.txt
└── TECHNICAL_REPORT.md   # explains how it works
```

## Libraries used

- GeoPandas - geographic data handling
- Plotly - interactive visualizations
- SciPy - KD-tree spatial indexing
- Pandas/NumPy - data processing

## Authors

Surya Jamuna Rani Subramaniyan (S3664414) & Govindharajulu Ramachandran (S3582361)

