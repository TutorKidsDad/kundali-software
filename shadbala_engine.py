"""Incremental Shadbala: no fabricated sixfold total."""
NATURAL={'Sun':60.,'Moon':360/7,'Venus':300/7,'Jupiter':240/7,'Mercury':180/7,'Mars':120/7,'Saturn':60/7}
EXALT={'Sun':10.,'Moon':33.,'Mars':298.,'Mercury':165.,'Jupiter':95.,'Venus':357.,'Saturn':200.}
BEST_HOUSE={'Sun':10,'Mars':10,'Moon':4,'Venus':4,'Mercury':1,'Jupiter':1,'Saturn':7}
COMPONENTS=('sthana_bala','dig_bala','kala_bala','cheshta_bala','naisargika_bala','drik_bala')
def shortest(a,b): return abs((a-b+180)%360-180)
OWN_SIGNS={'Sun':{4},'Moon':{3},'Mars':{0,7},'Mercury':{2,5},'Jupiter':{8,11},'Venus':{1,6},'Saturn':{9,10}}
SAPTAVARGA=(1,2,3,7,9,12,30)

# Natural (naisargika) planetary relationships used for dignity diagnostics.
# Values: +1 friend, 0 neutral, -1 enemy. Rahu/Ketu excluded.
NATURAL_RELATIONS={
 'Sun':{'Moon':1,'Mars':1,'Mercury':0,'Jupiter':1,'Venus':-1,'Saturn':-1},
 'Moon':{'Sun':1,'Mars':0,'Mercury':1,'Jupiter':0,'Venus':0,'Saturn':0},
 'Mars':{'Sun':1,'Moon':1,'Mercury':-1,'Jupiter':1,'Venus':0,'Saturn':0},
 'Mercury':{'Sun':1,'Moon':-1,'Mars':0,'Jupiter':0,'Venus':1,'Saturn':0},
 'Jupiter':{'Sun':1,'Moon':1,'Mars':1,'Mercury':-1,'Venus':-1,'Saturn':0},
 'Venus':{'Sun':-1,'Moon':-1,'Mars':0,'Mercury':1,'Jupiter':0,'Saturn':1},
 'Saturn':{'Sun':-1,'Moon':-1,'Mars':-1,'Mercury':1,'Jupiter':0,'Venus':1}}
SIGN_LORDS=('Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter')
RELATION_NAMES={-2:'great_enemy',-1:'enemy',0:'neutral',1:'friend',2:'great_friend'}
def temporary_friend(a,b):
    # Planet B in houses 2,3,4,10,11,12 from planet A.
    relative=(int(b//30)-int(a//30))%12+1
    return 1 if relative in (2,3,4,10,11,12) else -1
def compound_relationship(planet,other,lookup):
    if planet==other: return 'own'
    score=NATURAL_RELATIONS[planet][other]+temporary_friend(
        lookup[planet]['longitude'],lookup[other]['longitude'])
    return RELATION_NAMES[score]

SAPTAVARGA_POINTS={'moolatrikona':45.,'own':30.,'great_friend':22.5,'friend':15.,'neutral':7.5,'enemy':3.75,'great_enemy':1.875}
MOOLATRIKONA={'Sun':(4,0,20),'Moon':(1,4,30),'Mars':(0,0,12),'Mercury':(5,16,20),'Jupiter':(8,0,10),'Venus':(6,0,15),'Saturn':(10,0,20)}
def score_saptavargaja(name,longitude,placements):
    if set(placements)!={f'D{n}' for n in SAPTAVARGA}: return None
    total=0.
    for division in SAPTAVARGA:
        entry=placements[f'D{division}']; sign=entry['sign_index']; mt_sign,lo,hi=MOOLATRIKONA[name]
        if division==1 and sign==mt_sign and lo<=longitude%30<hi: dignity='moolatrikona'
        elif entry['own_sign']: dignity='own'
        else: dignity=entry['compound_relationship_to_lord']
        value=SAPTAVARGA_POINTS[dignity];entry['dignity']=dignity;entry['virupas']=value;total+=value
    return round(total,4)

def shadbala(planets, varga_sign_fn=None):

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
        # Saptavargaja *placement diagnostics* only. The final Bala requires
        # compound planetary friendships, exaltation/own/moolatrikona
        # classifications, and a chosen authoritative point schedule.
        varga_placements={}
        if varga_sign_fn is not None:
            for division in SAPTAVARGA:
                mapped=int(longitude//30) if division==1 else varga_sign_fn(longitude,division)
                varga_placements[f'D{division}']={'sign_index':mapped,
                    'sign_number':mapped+1,'own_sign':mapped in OWN_SIGNS[name]}
        relationships={other:compound_relationship(name,other,lookup)
                       for other in NATURAL_RELATIONS[name]}
        for placement in varga_placements.values():
            lord=SIGN_LORDS[placement['sign_index']]
            placement['sign_lord']=lord
            placement['compound_relationship_to_lord']=(
                'own' if lord==name else relationships[lord])
        saptavarga_score=score_saptavargaja(name,longitude,varga_placements) if varga_placements else None
        components={key:None for key in COMPONENTS}
        components['dig_bala']=round(dig,4)
        components['naisargika_bala']=round(natural,4)
        rows.append({'name':name,'components':components,
                     'sthana_subcomponents':{'saptavargaja_bala':saptavarga_score,'uchcha_bala':round(uchcha,4),'ojhayugma_bala':ojha,'kendradi_bala_whole_sign':kendradi,'drekkana_bala':drekkana},
                     'kala_subcomponents':{'paksha_bala':round(paksha,4)},
                     'calculated_partial_virupas':round(dig+natural+uchcha+kendradi+(ojha or 0)+drekkana+paksha+(saptavarga_score or 0),4),
                     'saptavargaja_diagnostics':{'planetary_relationships':relationships,'placements':varga_placements,'own_sign_count':sum(v['own_sign'] for v in varga_placements.values()),'bala_virupas':saptavarga_score,'status':'scored_pending_reference_validation' if saptavarga_score is not None else 'unavailable'},
                     'motion_diagnostics':{'longitude_speed_deg_per_day':lookup[name].get('longitude_speed_deg_per_day'), 'retrograde':lookup[name].get('retrograde')},
                     'total_virupas':None,'total_rupas':None,'meets_minimum':None})
    return {'status':'partial_not_validated','unit':'virupa',
            'note':'Incremental diagnostic only: Saptavargaja D1/D2/D3/D7/D9/D12/D30 placements and own-sign indicators added; Natural, temporary and compound friendships and sign lords are provided as diagnostics; Saptavargaja points use a declared Raman-style convention; reference-chart verification pending. Remaining Kala terms, Cheshta and Drik are NOT implemented. Dig and Kendradi use whole-sign approximations. Mercury/Saturn Ojhayugma remains unresolved. Paksha classification follows a stated convention (Mercury treated as benefic). Partial subtotal is NOT full Shadbala and MUST NOT be used for strength verdicts.',
            'planets':rows}
