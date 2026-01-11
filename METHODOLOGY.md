# Methodology

**Earthquake Exposure Analysis for Asian Cities**

Surya Jamuna Rani Subramaniyan (S3664414) & Govindharajulu Ramachandran (S3582361)  
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
- Plotly for interactive maps and all charts
- SciPy for the KD-tree
- Pandas and NumPy for data processing

### Visualizations:
The notebook generates 5 interactive charts:
1. Interactive risk map (dark theme with blue earthquakes, red cities)
2. Top 20 cities bar chart
3. PGA distribution histogram
4. Risk category pie chart
5. PGA attenuation with distance plot

---

## 5. Results

We ran the analysis on 1721 cities and 1263 earthquakes from 2025. Here's what we found:

### How many cities in each risk category:
- CRITICAL: 1 city
- MODERATE: 4 cities
- LOW: 15 cities
- MINIMAL: 1701 cities (basically everyone else)

Most cities are minimal risk which makes sense - not everywhere has earthquakes nearby.

### Cities with highest risk:
1. Mandalay, Myanmar (PGA = 2.46g) - this one was really high, probably because of a big earthquake nearby
2. Hualien, Taiwan (PGA = 0.19g)
3. Banda Aceh, Indonesia (PGA = 0.16g)
4. Miyazaki, Japan (PGA = 0.16g)
5. Naypyidaw, Myanmar (PGA = 0.12g)

### What we noticed:
- Myanmar had the highest risk cities, probably due to some big earthquakes there in 2025
- Taiwan and Indonesia are on the Ring of Fire so it makes sense they show up
- Japan has lots of earthquakes but the big cities aren't always right next to them
- The KD-tree thing really sped up the analysis - way faster than checking every city against every earthquake one by one

---

## 6. Limitations

There are some things our analysis doesn't handle well:

### Data limitations:
- We only looked at earthquakes from 2025, so cities that had big earthquakes in previous years might not show up as high risk
- The city data treats each city as a single point, but in reality cities are spread out over a large area
- Some smaller cities might not be in the dataset we used

### Method limitations:
- The PGA formula we used is pretty simplified compared to what actual earthquake engineers use. They have way more complex models that consider things like soil type and building foundations
- We assume all earthquakes affect cities the same way, but really the type of fault and direction of shaking matters too
- Our search radius formula is an approximation - real felt distance depends on lots of factors (soil type, fault direction, local geology, building type)

### What we would do differently next time:
- Use multiple years of data to get a better picture
- Maybe include data about building quality in different cities
- Try using a more advanced GMPE model if we had more time

---

## 7. References

1. Campbell, K. W., & Bozorgnia, Y. (2008). NGA ground motion model. Earthquake Spectra.
2. USGS Earthquake Catalog: https://earthquake.usgs.gov/
3. Natural Earth populated places dataset

---
