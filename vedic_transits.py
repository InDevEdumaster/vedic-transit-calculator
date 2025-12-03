import swisseph as swe
import datetime
import os
import math

# ==========================================
# CONFIGURATION
# ==========================================
EPHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe')

# Planets to calculate
# Format: (swisseph_id, "Name")
PLANETS = [
    (swe.SUN, "Sun"),
    (swe.MOON, "Moon"),
    (swe.MARS, "Mars"),
    (swe.MERCURY, "Mercury"),
    (swe.JUPITER, "Jupiter"),
    (swe.VENUS, "Venus"),
    (swe.SATURN, "Saturn"),
    (swe.MEAN_NODE, "Rahu"), # Mean Node = Rahu
    # Ketu is calculated relative to Rahu
]

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def setup_swisseph():
    """Configures Swiss Ephemeris settings."""
    # Set path to ephemeris files
    swe.set_ephe_path(EPHE_PATH)
    
    # Set Sidereal Mode to True Chitra Paksha (Lahiri)
    # SIDM_LAHIRI (1) is the standard constant for Chitra Paksha
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

def get_julian_day(dt):
    """Converts a python datetime to Julian Day (UT)."""
    return swe.utc_to_jd(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second + dt.microsecond / 1e6, 1)[1]

def get_datetime_from_jd(jd):
    """Converts Julian Day (UT) back to python datetime."""
    # result is (y, m, d, h, min, s)
    res = swe.jdut1_to_utc(jd, 1)
    y, m, d, h, mi, s = res
    # Handle seconds carefully to avoid float rounding errors in display
    micros = int((s - int(s)) * 1e6)
    return datetime.datetime(int(y), int(m), int(d), int(h), int(mi), int(s), micros)

def get_planet_data(jd, planet_id):
    """
    Returns (longitude, speed, is_retrograde) for a given planet at a given JD.
    Uses Mean Nodes for Rahu/Ketu.
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    if planet_id == "KETU":
        # Ketu is Rahu + 180 degrees
        # Get Rahu data first
        res = swe.calc_ut(jd, swe.MEAN_NODE, flags)
        
        # Unpack result: ((lon, lat, dist, speed_lon, ...), rflags)
        rahu_data = res[0]
        rahu_lon = rahu_data[0]
        rahu_speed = rahu_data[3] # Speed is same magnitude usually
        
        ketu_lon = (rahu_lon + 180.0) % 360.0
        # Rahu/Ketu Mean nodes are always retrograde mathematically (negative speed)
        # or rarely stationary. 
        is_retro = rahu_speed < 0 
        return ketu_lon, rahu_speed, is_retro
    else:
        res = swe.calc_ut(jd, planet_id, flags)
        
        # Unpack result: ((lon, lat, dist, speed_lon, ...), rflags)
        data = res[0]
        lon = data[0]
        speed = data[3]
        
        is_retro = speed < 0
        return lon, speed, is_retro

def get_sign(lon):
    """Returns sign index (1-12) from longitude."""
    return int(lon / 30) + 1

def get_house(sign_num, asc_num):
    """Calculates Whole Sign House (1-12)."""
    h = (sign_num - asc_num + 12) % 12 + 1
    return h

def format_date(dt):
    """Formats datetime for display."""
    return dt.strftime("%d-%b-%Y %H:%M")

def find_events(planet_id, start_jd, end_jd):
    """
    Scans the time range to find 'events' (Sign Changes or Motion Changes).
    Returns a list of dictionaries containing state data at specific times.
    """
    events = []
    
    # Initial State
    current_jd = start_jd
    curr_lon, curr_speed, curr_retro = get_planet_data(current_jd, planet_id)
    curr_sign = get_sign(curr_lon)
    
    # Add start point
    events.append({
        'jd': current_jd,
        'sign': curr_sign,
        'retro': curr_retro,
        'speed': curr_speed
    })
    
    # Scan parameters
    # For fast planets (Moon), we need smaller steps. 
    # For others, 6 hours is usually safe to detect sign entry, 
    # but we will use binary search refinement.
    step_days = 0.25 # 6 hours
    if planet_id == swe.MOON:
        step_days = 0.04 # ~1 hour
        
    scan_jd = start_jd
    
    while scan_jd < end_jd:
        prev_jd = scan_jd
        prev_lon = curr_lon
        prev_retro = curr_retro
        prev_sign = curr_sign
        
        scan_jd += step_days
        if scan_jd > end_jd:
            scan_jd = end_jd
            
        curr_lon, curr_speed, curr_retro = get_planet_data(scan_jd, planet_id)
        curr_sign = get_sign(curr_lon)
        
        # Check for State Change
        sign_changed = curr_sign != prev_sign
        motion_changed = curr_retro != prev_retro
        
        if sign_changed or motion_changed:
            # REFINE TIME using Binary Search
            # We want to find the exact moment the state changed between prev_jd and scan_jd
            
            low = prev_jd
            high = scan_jd
            found_jd = high
            
            # Precision loop (down to ~1 second)
            for _ in range(20):
                mid = (low + high) / 2
                m_lon, m_speed, m_retro = get_planet_data(mid, planet_id)
                m_sign = get_sign(m_lon)
                
                # Logic: Did the change happen in the first half?
                # We check if the state at 'mid' matches the 'prev' state.
                # If matches, change is in upper half. If not, change is in lower half.
                
                # Check what type of change we are looking for.
                # If both happened, we prioritize the earlier one implicitly by narrowing down.
                # But usually, they don't happen exact same second.
                
                match_prev = (m_sign == prev_sign) if sign_changed else True
                if motion_changed:
                    match_prev = match_prev and (m_retro == prev_retro)
                
                if match_prev:
                    low = mid
                else:
                    high = mid
                    found_jd = mid # This is a candidate for the change time
            
            # Register the event
            # Get precise properties at the found time
            f_lon, f_speed, f_retro = get_planet_data(found_jd, planet_id)
            f_sign = get_sign(f_lon)
            
            events.append({
                'jd': found_jd,
                'sign': f_sign,
                'retro': f_retro,
                'speed': f_speed
            })
            
            # Reset loop vars to the event found to ensure we don't skip a double event 
            # (though unlikely in 6 hrs)
            scan_jd = found_jd 
            curr_lon, curr_speed, curr_retro = f_lon, f_speed, f_retro
            curr_sign = f_sign
            
            # Add a tiny epsilon to scan_jd so we don't find the same event again
            scan_jd += 0.0001 

    # Add end point closure if not exactly on end
    if events[-1]['jd'] < end_jd:
         # Just to close the loop
         pass
         
    return events

# ==========================================
# MAIN SCRIPT
# ==========================================

def main():
    print("="*60)
    print("      VEDIC PLANETARY TRANSITS CALCULATOR (SWISSEPH)      ")
    print("="*60)
    print("Configuration:")
    print(f"Ephemeris Path: {EPHE_PATH}")
    print("Ayanamsa:       True Chitra Paksha (Lahiri)")
    print("Nodes:          Mean Nodes")
    print("Positions:      Geocentric, True")
    print("Timeframe:      +/- 1 Year from NOW")
    print("-" * 60)

    try:
        setup_swisseph()
    except swe.Error as e:
        print(f"ERROR: Could not initialize Swiss Ephemeris.\n{e}")
        print(f"Make sure swisseph files are in: {EPHE_PATH}")
        input("Press Enter to exit...")
        return

    # User Input
    while True:
        try:
            asc_input = input("Enter Ascendant Sign Number (1-12): ").strip()
            asc_num = int(asc_input)
            if 1 <= asc_num <= 12:
                break
            print("Invalid number. Please enter 1 for Aries, 2 for Taurus, etc.")
        except ValueError:
            print("Please enter a valid integer.")

    print(f"\nCalculations based on Ascendant: {ZODIAC_SIGNS[asc_num-1]} ({asc_num})")
    print("Generating tables... Please wait.\n")

    # Timeframe definition
    now = datetime.datetime.now()
    start_dt = now - datetime.timedelta(days=365)
    end_dt = now + datetime.timedelta(days=365)
    
    start_jd = get_julian_day(start_dt)
    end_jd = get_julian_day(end_dt)
    now_jd = get_julian_day(now)

    # Process standard planets
    all_planets = PLANETS.copy()
    all_planets.append(("KETU", "Ketu")) # Add Ketu manually to list

    for pid, pname in all_planets:
        print(f"Processing {pname}...")
        
        # Calculate events (Sign changes and Motion changes)
        events = find_events(pid, start_jd, end_jd)
        
        # Display Table Header
        print(f"\nTABLE: {pname.upper()}")
        print("-" * 110)
        print(f"{'START DATE & TIME':<20} | {'SIGN':<12} | {'HOUSE':<5} | {'MOTION':<10} | {'END DATE & TIME':<20} | {'STATUS':<8}")
        print("-" * 110)
        
        # Iterate through events to build rows
        # Row N is from Event N to Event N+1
        for i in range(len(events)):
            current_event = events[i]
            
            # Start Time
            t_start = current_event['jd']
            dt_start = get_datetime_from_jd(t_start)
            
            # State
            sign_idx = current_event['sign']
            sign_name = ZODIAC_SIGNS[sign_idx-1]
            house_num = get_house(sign_idx, asc_num)
            is_retro = current_event['retro']
            motion_str = "Retrograde" if is_retro else "Direct"
            
            # End Time
            if i < len(events) - 1:
                t_end = events[i+1]['jd']
                dt_end = get_datetime_from_jd(t_end)
                dt_end_str = format_date(dt_end)
            else:
                t_end = end_jd
                dt_end = end_dt
                dt_end_str = format_date(dt_end)

            # Status Check
            # Allow a small epsilon for "Current" to handle current second matches
            status = ""
            if t_end < now_jd:
                status = "Past"
            elif t_start > now_jd:
                status = "Future"
            else:
                status = "<< CUR >>"
            
            # Determine row color/highlight logic (optional, just text here)
            # Printing the row
            start_str = format_date(dt_start)
            
            # Clean up the start string for the very first row
            # Removed (Start) and (End) text as requested

            print(f"{start_str:<20} | {sign_name:<12} | {house_num:<5} | {motion_str:<10} | {dt_end_str:<20} | {status:<8}")

        print("\n")

    # ==========================================
    # CURRENT TRANSIT SNAPSHOT
    # ==========================================
    print("\n" + "="*115)
    print(f"      CURRENT TRANSITS SNAPSHOT ({format_date(now)})")
    print("="*115)
    print(f"{'PLANET':<8} | {'SIGN':<10} | {'HSE':<3} | {'MOTION':<8} | {'EXACT POSITION':<16} | {'START DATE & TIME':<18} | {'END DATE & TIME':<18}")
    print("-" * 115)

    for pid, pname in all_planets:
        # Get Current Exact Position
        curr_lon, curr_speed, curr_retro = get_planet_data(now_jd, pid)
        sign_idx = get_sign(curr_lon)
        sign_name = ZODIAC_SIGNS[sign_idx-1]
        house_num = get_house(sign_idx, asc_num)
        
        # Calculate degrees within sign for display
        deg_in_sign = curr_lon % 30
        d_str = f"{int(deg_in_sign)}° {int((deg_in_sign % 1) * 60)}'"
        
        motion_str = "Retro" if curr_retro else "Direct"
        
        # Find Duration (Start and End of current state)
        # We need to scan events again for this specific planet to find where 'now' fits
        events = find_events(pid, start_jd, end_jd)
        
        start_str = "Unknown"
        end_str = "Unknown"
        
        for i in range(len(events)):
            t_s = events[i]['jd']
            # If it's the last event, it goes to end_jd
            t_e = events[i+1]['jd'] if i < len(events) - 1 else end_jd
            
            if t_s <= now_jd <= t_e:
                start_str = format_date(get_datetime_from_jd(t_s))
                end_str = format_date(get_datetime_from_jd(t_e))
                break
        
        print(f"{pname:<8} | {sign_name:<10} | {house_num:<3} | {motion_str:<8} | {d_str:<16} | {start_str:<18} | {end_str:<18}")

    print("-" * 115)
    print("\n")

    input("Calculations complete. Press Enter to exit.")

if __name__ == "__main__":
    main()