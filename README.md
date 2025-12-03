# Vedic Transit Calculator

A precise, terminal-based Python tool for calculating Vedic Astrology planetary transits.

This script utilizes the Swiss Ephemeris (via `pyswisseph`) to compute exact planetary positions, sign ingresses, and motion changes (Retrograde/Direct) with high astronomical accuracy.

---

## Output Preview

<img src="screenshot.png" width="750">

---

## Features

* **Calculates Transits:** Generates timelines for sign changes and motion changes (Retrograde/Direct).
* **Vedic Settings:**

  * Ayanamsa: True Chitra Paksha (Lahiri)
  * Nodes: Mean Nodes (Rahu/Ketu)
  * Positions: Geocentric, True positions
* **Customizable Timeframe:** Defaults to ±1 year from the current date
* **Whole Sign Houses:** Calculates house positions based on the selected Ascendant (Lagna)
* **Current Snapshot:** Displays real-time planetary positions at execution

---

## Prerequisites

* Python 3.6+
* `pyswisseph` library

---

## Installation

### Clone the repository

```bash
git clone https://github.com/yourusername/vedic-transit-calculator.git
cd vedic-transit-calculator
```

### Install Dependencies

```bash
pip install pyswisseph
```

### Ephemeris Files (Already Included)

The **ephe/** directory and `.se1` Swiss Ephemeris data files are already uploaded in this repository.

If you need additional year ranges in the future, download more `.se1` files from the Swiss Ephemeris download area and place them inside the **ephe** folder.

---

## Directory Structure

```
vedic-transit-calculator/
├── ephe/
│   ├── sepl_18.se1
│   ├── semo_18.se1
│   └── ... (other ephemeris files)
├── vedic_transits.py
├── screenshot.png
├── README.md
└── .gitignore
```

---

## Usage

Run the script:

```bash
python vedic_transits.py
```

The script will:

1. Initialize the Swiss Ephemeris (using the included `ephe` folder)
2. Ask for your Ascendant (Lagna) sign number

   * Example: `1` = Aries, `5` = Leo
3. Generate detailed transit tables for all nine planets
4. Display a real-time planetary snapshot

---

## License

This project is licensed under the **GNU General Public License v3.0**.
See the **LICENSE** file for details.
