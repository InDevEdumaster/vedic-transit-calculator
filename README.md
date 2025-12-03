Vedic Transit Calculator

A precise, terminal-based Python tool for calculating Vedic Astrology planetary transits.

This script utilizes the Swiss Ephemeris (via pyswisseph) to calculate exact planetary positions, sign ingresses, and changes in motion (Retrograde/Direct) with high astronomical accuracy.

Features

Calculates Transits: Generates timelines for Sign changes and Motion changes (Retrograde/Direct).

Vedic Settings: - Ayanamsa: True Chitra Paksha (Lahiri).

Nodes: Mean Nodes (Rahu/Ketu).

Positions: Geocentric, True positions.

Customizable Timeframe: Defaults to +/- 1 year from the current date.

Whole Sign Houses: Calculates house positions based on the user-selected Ascendant (Lagna).

Current Snapshot: Displays a real-time snapshot of planetary positions at the moment of execution.

Prerequisites

Python 3.6+

pyswisseph library

Installation

Clone the repository:

git clone [https://github.com/yourusername/vedic-transit-calculator.git](https://github.com/yourusername/vedic-transit-calculator.git)
cd vedic-transit-calculator


Install Dependencies:

pip install pyswisseph


Setup Ephemeris Files:
This tool requires Swiss Ephemeris data files to function.

Create a folder named ephe in the root directory of this project.

Download the ephemeris files (files ending in .se1) from the Swiss Ephemeris Download Area.

At minimum, you need the files for the years you plan to calculate (e.g., sepl_18.se1 for 1800-2400 AD).

Place these .se1 files inside the ephe folder.

Directory Structure:

vedic-transit-calculator/
├── ephe/
│   ├── sepl_18.se1
│   ├── semo_18.se1
│   └── ...
├── vedic_transits.py
├── README.md
└── .gitignore


Usage

Run the script using Python:

python vedic_transits.py


The script will initialize the Swiss Ephemeris.

Enter the number corresponding to your Ascendant (Lagna) sign (e.g., 1 for Aries, 5 for Leo).

The script will output detailed transit tables for all 9 planets and a current snapshot.

License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
