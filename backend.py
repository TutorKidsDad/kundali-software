from datetime import datetime, timezone
from analysis_engine import analyze
from shadbala_engine import shadbala
from report_engine import build_report
from fastapi.responses import Response
from ashtakavarga_engine import ashtakavarga
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import math
import json
from pathlib import Path
import swisseph as swe
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title='Kundli Explorer API', version='1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['GET','POST'], allow_headers=['*'])
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
NAK = ['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
BODIES = [('Sun',swe.SUN),('Moon',swe.MOON),('Mars',swe.MARS),('Mercury',swe.MERCURY),('Jupiter',swe.JUPITER),('Venus',swe.VENUS),('Saturn',swe.SATURN)]

import re
# Source mappings from the user's original divisional workbook.
TABLES = json.loads((Path(__file__).resolve().parent / 'varga_tables.json').read_text(encoding='utf-8'))
DIVISIONS = [2,3,4,7,9,10,12,16,20,24,30,40,45,60]
ALIASES = {'ar':0,'ari':0,'aries':0,'ta':1,'tau':1,'taurus':1,'ge':2,'gem':2,'gemini':2,'cn':3,'ca':3,'can':3,'cancer':3,'le':4,'leo':4,'vi':5,'vir':5,'virgo':5,'li':6,'lib':6,'libra':6,'sc':7,'sco':7,'scorpio':7,'sa':8,'sg':8,'sag':8,'sagittarius':8,'cp':9,'cap':9,'capricorn':9,'aq':10,'aqu':10,'aquarius':10,'pi':11,'pis':11,'pisces':11}

def parse_sign(value):
    token = str(value).strip().lower()
    if token in ALIASES: return ALIASES[token]
    # D2 contains descriptive entries, e.g. SUN (LEO).
    for word in re.findall(r'[a-z]+',token)[::-1]:
        if word in ALIASES: return ALIASES[word]
    raise ValueError(f'Unrecognized sign in workbook: {value!r}')

def varga_sign(longitude, division):
    if division not in DIVISIONS: raise ValueError(f'Unsupported division: {division}')
    lon = longitude % 360
    rashi = int(lon // 30)
    within = lon - rashi * 30
    rows = TABLES[f'D{division}']
    if division == 30:
        # Unequal Trimsamsa segments: odd 5/5/8/7/5; even reversed 5/7/8/5/5.
        odd = rashi % 2 == 0
        bounds = [5,10,18,25,30] if odd else [5,12,20,25,30]
        part = next(i for i,b in enumerate(bounds) if within < b)
        # Separate odd/even sections in the workbook.
        section = 1 if odd else next(i for i,row in enumerate(rows) if row and 'even signs' in str(row[0]).lower())
        candidates = [row for row in rows[section+1:] if row and str(row[0]).strip() == str(float(part+1))]
        if not candidates: raise ValueError('D30 workbook mapping not found')
        return parse_sign(candidates[0][3])
    part = min(division-1,int(within * division / 30))
    if division in (2,3,4,7,9):
        return parse_sign(rows[rashi+1][part+1])
    if division in (10,12,16,20,40):
        return parse_sign(rows[part+1][rashi+1])
    if division == 24:
        return parse_sign(rows[part+1][2 if rashi % 2 == 0 else 3])
    if division == 45:
        return parse_sign(rows[part+1][2 + (rashi % 3)])
    if division == 60:
        return parse_sign(rows[part+1][rashi+2])
    raise ValueError('Unsupported mapping')

def build_varga(planets, division):
    asc_sign = varga_sign(planets[0]['longitude'], division)
    mapped=[]
    for p in planets:
        idx = varga_sign(p['longitude'], division)
        # Longitude within the subdivisional sign is a display convention;
        # unequal D30 is intentionally not assigned a misleading degree.
        degree = None if division == 30 else round(((p['longitude'] % 30) * division) % 30,5)
        mapped.append(dict(p,sign_index=idx,sign=SIGNS[idx],house=(idx-asc_sign)%12+1,degree=degree))
    return {'division':division,'ascendant_sign':SIGNS[asc_sign],'planets':mapped}

# Vimshottari periods use the conventional 120-year cycle and a configurable
# fixed 365.25-day dasha year. Other calendar-year conventions differ.
from datetime import timedelta
DASHA_LORDS = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury']
DASHA_YEARS = {'Ketu':7,'Venus':20,'Sun':6,'Moon':10,'Mars':7,'Rahu':18,'Jupiter':16,'Saturn':19,'Mercury':17}
DASHA_YEAR_DAYS = 365.25

def vimshottari(moon_longitude, birth_utc):
    span = 360.0 / 27.0
    position = (moon_longitude % 360) / span
    nak_index = int(position) % 27
    fraction_elapsed = position - int(position)
    start_lord_idx = nak_index % 9
    first_lord = DASHA_LORDS[start_lord_idx]
    # Anchor the entire cycle at the beginning of the Moon's birth nakshatra.
    start = birth_utc - timedelta(days=fraction_elapsed * DASHA_YEARS[first_lord] * DASHA_YEAR_DAYS)
    def iso(t): return t.isoformat(timespec='seconds')
    def subperiods(parent_start, parent_duration_days, lord_index, depth):
        cursor = parent_start
        output = []
        for offset in range(9):
            idx = (lord_index + offset) % 9
            lord = DASHA_LORDS[idx]
            duration = parent_duration_days * DASHA_YEARS[lord] / 120
            end = cursor + timedelta(days=duration)
            entry = {'lord':lord,'start_utc':iso(cursor),'end_utc':iso(end)}
            if depth > 1:
                entry['pratyantardashas'] = subperiods(cursor,duration,idx,1)
            output.append(entry)
            cursor = end
        return output
    periods = []
    cursor = start
    for offset in range(9):
        idx = (start_lord_idx + offset) % 9
        lord = DASHA_LORDS[idx]
        days = DASHA_YEARS[lord] * DASHA_YEAR_DAYS
        end = cursor + timedelta(days=days)
        periods.append({'lord':lord,'years':DASHA_YEARS[lord],
                        'start_utc':iso(cursor),'end_utc':iso(end),
                        'antardashas':subperiods(cursor,days,idx,2)})
        cursor = end
    return {'system':'Vimshottari','year_days':DASHA_YEAR_DAYS,
            'date_basis':'UTC instants; display in birth time zone',
            'birth_nakshatra':NAK[nak_index],
            'birth_nakshatra_lord':first_lord,
            'balance_at_birth_years':round((1-fraction_elapsed)*DASHA_YEARS[first_lord],8),
            'mahadashas':periods}

class Birth(BaseModel):
    name: str = ''
    date: str
    time: str
    place: str = ''
    latitude: float = Field(ge=-89.99, le=89.99)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = 'Asia/Kolkata'
    ayanamsha: str = 'lahiri'
    nodes: str = 'mean'

def details(name, longitude, speed, lagna_sign):
    longitude %= 360
    sign_index = int(longitude // 30)
    nak_index = min(26,int(longitude / (360 / 27)))
    pada = min(4,int((longitude % (360/27)) / (360/108)) + 1)
    return dict(name=name, longitude=round(longitude,7), sign=SIGNS[sign_index], sign_index=sign_index,
                degree=round(longitude%30,5), house=(sign_index-lagna_sign)%12+1,
                nakshatra=NAK[nak_index], pada=pada, retrograde=speed < 0)

@app.get('/api/health')
def health(): return {'ok':True, 'ephemeris':swe.version}

@app.post('/api/chart')
def chart(b: Birth):
    try:
        if b.ayanamsha != 'lahiri' or b.nodes not in ('mean','true'):
            raise ValueError('Unsupported ayanamsha or lunar node setting')
        dt = datetime.fromisoformat(f'{b.date}T{b.time}')
        local = dt.replace(tzinfo=ZoneInfo(b.timezone))
        # Reject ambiguous and nonexistent local times rather than silently calculating wrong charts.
        utc0 = local.replace(fold=0).astimezone(timezone.utc)
        utc1 = local.replace(fold=1).astimezone(timezone.utc)
        if utc0 != utc1:
            raise ValueError('Ambiguous local time due to daylight saving transition; choose a different time or resolve the offset')
        if utc0.astimezone(ZoneInfo(b.timezone)).replace(tzinfo=None) != dt:
            raise ValueError('Nonexistent local time due to daylight saving transition')
        utc = utc0
        jd = swe.julday(utc.year,utc.month,utc.day,utc.hour+utc.minute/60+utc.second/3600)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        cusps, ascmc = swe.houses_ex(jd,b.latitude,b.longitude,b'P',flags=swe.FLG_SIDEREAL)
        asc = ascmc[0] % 360
        lagna_sign = int(asc//30)
        planets = [details('Ascendant',asc,0,lagna_sign)]
        for name, body in BODIES:
            pos, returned = swe.calc_ut(jd,body,flags)
            if not (returned & swe.FLG_SIDEREAL):
                raise RuntimeError('Sidereal ephemeris calculation failed')
            planets.append(details(name,pos[0],pos[3],lagna_sign))
        node_id = swe.MEAN_NODE if b.nodes == 'mean' else swe.TRUE_NODE
        pos, returned = swe.calc_ut(jd,node_id,flags)
        rahu = pos[0]%360
        planets.append(details('Rahu',rahu,pos[3],lagna_sign))
        planets.append(details('Ketu',(rahu+180)%360,pos[3],lagna_sign))
        return {'name':b.name,'place':b.place,'date_of_birth':b.date,'time_of_birth':b.time,
                'timezone':b.timezone,'latitude':b.latitude,'longitude':b.longitude,
                'local_time':local.isoformat(),'utc_time':utc.isoformat(),
                'julian_day_ut':jd,'ayanamsha':'Lahiri','ayanamsha_degrees':round(swe.get_ayanamsa_ut(jd),7),
                'nodes':b.nodes,'house_system':'Whole sign (Rashi)','ephemeris':'Swiss Ephemeris Moshier',
                'ascendant_sign':SIGNS[lagna_sign], 'planets':planets,
                'analysis':analyze(planets),
                'shadbala':shadbala(planets),
                'ashtakavarga':ashtakavarga(planets),
                'vimshottari':vimshottari(next(p['longitude'] for p in planets if p['name']=='Moon'),utc),
                'vargas': {f'D{d}':build_varga(planets,d) for d in DIVISIONS}, 'available_vargas':[f'D{d}' for d in DIVISIONS]}
    except (ValueError,ZoneInfoNotFoundError,OverflowError) as exc:
        raise HTTPException(status_code=422,detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500,detail=f'Calculation failed: {exc}')

app.mount('/', StaticFiles(directory=str(Path(__file__).resolve().parent),html=True),name='frontend')


@app.post('/api/report/pdf')
def report_pdf(b: Birth):
    data = chart(b)
    content = build_report(data)
    return Response(content=content,media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="kundli-complete.pdf"'})
