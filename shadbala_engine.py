"""Incremental Shadbala: no fabricated sixfold total."""
NATURAL={'Sun':60.,'Moon':360/7,'Venus':300/7,'Jupiter':240/7,'Mercury':180/7,'Mars':120/7,'Saturn':60/7}
EXALT={'Sun':10.,'Moon':33.,'Mars':298.,'Mercury':165.,'Jupiter':95.,'Venus':357.,'Saturn':200.}
BEST_HOUSE={'Sun':10,'Mars':10,'Moon':4,'Venus':4,'Mercury':1,'Jupiter':1,'Saturn':7}
COMPONENTS=('sthana_bala','dig_bala','kala_bala','cheshta_bala','naisargika_bala','drik_bala')
def shortest(a,b): return abs((a-b+180)%360-180)
def shadbala(planets):
    lookup={p['name']:p for p in planets}
    asc=lookup['Ascendant']['longitude']
    rows=[]
    for name,natural in NATURAL.items():
        longitude=lookup[name]['longitude']
        uchcha=(180-shortest(longitude,EXALT[name]))/3
        best=(asc+30*(BEST_HOUSE[name]-1))%360
        dig=(180-shortest(longitude,best))/3
        # Ojhayugma: odd signs and odd navamshas for Sun/Mars/Jupiter;
        # even signs and even navamshas for Moon/Venus. Mercury and Saturn
        # have variant traditions, so do not assign their Ojhayugma score.
        sign=int(longitude//30)
        navamsha=int((longitude%30)//(30/9))
        nav_sign=(sign*9+navamsha)%12
        preference={'Sun':0,'Mars':0,'Jupiter':0,'Moon':1,'Venus':1}
        ojha=None
        if name in preference:
            target=preference[name]
            ojha=15*(int(sign%2==target)+int(nav_sign%2==target))
        # Kendradi (whole-sign house approximation; not quadrant bhava).
        house=int(lookup[name]['house'])
        kendradi=60 if house in (1,4,7,10) else 30 if house in (2,5,8,11) else 15
        # Drekkana Bala: masculine planets first decanate, neutral planets
        # second, feminine planets third; exact 0/15 virupas.
        decanate=min(2,int((longitude % 30)/10))
        preferred_decanate={'Sun':0,'Mars':0,'Jupiter':0,
                            'Mercury':1,'Saturn':1,'Moon':2,'Venus':2}[name]
        drekkana=15 if decanate==preferred_decanate else 0
        # Paksha Bala depends on Sun-Moon elongation, not on calendar tithi
        # rounded to an integer. Waxing benefic and waning malefic convention.
        elongation=(lookup['Moon']['longitude']-lookup['Sun']['longitude'])%360
        illuminated_phase=(180-abs(elongation-180))/3
        waxing_benefic={'Moon','Mercury','Jupiter','Venus'}
        paksha=illuminated_phase if name in waxing_benefic else 60-illuminated_phase
        components={key:None for key in COMPONENTS}
        components['dig_bala']=round(dig,4)
        components['naisargika_bala']=round(natural,4)
        rows.append({'name':name,'components':components,
                     'sthana_subcomponents':{'uchcha_bala':round(uchcha,4),'ojhayugma_bala':ojha,'kendradi_bala_whole_sign':kendradi,'drekkana_bala':drekkana},
                     'kala_subcomponents':{'paksha_bala':round(paksha,4)},
                     'calculated_partial_virupas':round(dig+natural+uchcha+kendradi+(ojha or 0)+drekkana+paksha,4),
                     'motion_diagnostics':{'longitude_speed_deg_per_day':lookup[name].get('longitude_speed_deg_per_day'), 'retrograde':lookup[name].get('retrograde')},
                     'total_virupas':None,'total_rupas':None,'meets_minimum':None})
    return {'status':'partial_not_validated','unit':'virupa',
            'note':'Incremental diagnostic only: Drekkana Bala and Paksha Bala added. Saptavargaja, remaining Kala terms, Cheshta and Drik are NOT implemented. Dig and Kendradi use whole-sign approximations. Mercury/Saturn Ojhayugma remains unresolved. Paksha classification follows a stated convention (Mercury treated as benefic). Partial subtotal is NOT full Shadbala and MUST NOT be used for strength verdicts.',
            'planets':rows}
