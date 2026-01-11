# Methodology

**Earthquake Exposure Analysis for Asian Cities**

Surya Jamuna Rani Subramanian & Govindharajulu Ramachandran  
Scientific Programming for Geospatial Sciences  
January 2026

---

## 1. Introduction

For this assignment, we wanted to figure out which cities in Asia are most at risk from earthquakes. Instead of just looking at how close cities are to earthquakes, we used something called Peak Ground Acceleration (PGA) which is what engineers actually use to measure earthquake impact.

The main goal was to:
- Get earthquake data from USGS
- Calculate PGA values for each city
- Make some nice visualizations to show the results

---

## 2. Data Sources

### Earthquake Data
We used the USGS Earthquake Catalog API to get all the earthquakes in Asia for 2025. We filtered for magnitude 5.0 and above since smaller ones don't really affect cities much.

- Region: Asia (roughly -10° to 80° latitude, 25° to 180° longitude)
- Time period: All of 2025
- Minimum magnitude: 5.0

### City Data
For cities, we used Natural Earth's populated places dataset. We only looked at cities with population over 250,000 since those are the major urban areas.

---

## 3. How We Did It

### 3.1 PGA Calculation

PGA stands for Peak Ground Acceleration. It tells you how much the ground shakes during an earthquake. We used this formula from Campbell and Bozorgnia (2008):

```
log10(PGA) = -1.8 + 0.6*M - 1.8*log10(R + 1) - 0.003*(R + 1)
```

Where:
- M = earthquake magnitude
- R = distance to the earthquake (in km)

The distance R includes depth, so we calculate it as:
```
R = sqrt(horizontal_distance^2 + depth^2)
```

This is important because shallow earthquakes are way more dangerous than deep ones.

### 3.2 Finding Nearby Earthquakes (KD-Trees)

Instead of checking every city against every earthquake (which would be super slow), we used a KD-Tree. This is basically a smart way to organize points so you can quickly find which ones are nearby.

We also made the search radius depend on the earthquake magnitude - bigger earthquakes can affect cities further away. The formula we used is:

```
Radius = 10^(0.5*M - 0.5) km
```

So for example:
- M5.0 earthquake: ~100 km radius
- M7.0 earthquake: ~1000 km radius

### 3.3 Risk Categories

Based on the max PGA value for each city, we put them into categories:

| PGA Value | Category | What it means |
|-----------|----------|---------------|
| >= 0.5g | CRITICAL | Serious damage likely |
| 0.3-0.5g | HIGH | Moderate to heavy damage |
| 0.1-0.3g | MODERATE | People feel it, minor damage |
| 0.02-0.1g | LOW | Some people feel it |
| < 0.02g | MINIMAL | Barely noticeable |

---

## 4. Implementation

We wrote the code in Python and split it into different files:

- `acquire.py` - downloads the earthquake and city data
- `preprocess.py` - cleans up the data and projects it
- `spatial_index.py` - the KD-tree stuff
- `metrics.py` - calculates PGA values
- `viz.py` - makes the maps and charts

The main analysis runs in a Jupyter notebook (`exploration.ipynb`).

### Libraries we used:
- GeoPandas for the geographic data
- Plotly for interactive maps
- SciPy for the KD-tree
- Pandas and NumPy for data processing

---

## 5. Results

After running the analysis on 2025 earthquake data, we found that cities in Japan and Indonesia tend to have the highest risk because they're close to where big earthquakes happen.

The KD-tree made the analysis much faster - instead of doing hundreds of thousands of distance checks, it only needed a few thousand.

---

## 6. Problems and Future Work

Some things we could improve:
- The PGA formula we used is simplified. Real engineers use more complex ones
- We treat cities as single points but they're actually spread out areas
- We only looked at one year of data

---

## 7. References

1. Campbell, K. W., & Bozorgnia, Y. (2008). NGA ground motion model. Earthquake Spectra.
2. USGS Earthquake Catalog: https://earthquake.usgs.gov/
3. Natural Earth populated places dataset

---
