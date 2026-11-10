"""Incremental Shadbala: no fabricated sixfold total."""
NATURAL={'Sun':60.,'Moon':360/7,'Venus':300/7,'Jupiter':240/7,'Mercury':180/7,'Mars':120/7,'Saturn':60/7}
EXALT={'Sun':10.,'Moon':33.,'Mars':298.,'Mercury':165.,'Jupiter':95.,'Venus':357.,'Saturn':200.}
BEST_HOUSE={'Sun':10,'Mars':10,'Moon':4,'Venus':4,'Mercury':1,'Jupiter':1,'Saturn':7}
COMPONENTS=('sthana_bala','dig_bala','kala_bala','cheshta_bala','naisargika_bala','drik_bala')
MINIMUM_VIRUPAS={'Sun':390.,'Moon':360.,'Mars':300.,'Mercury':420.,'Jupiter':390.,'Venus':330.,'Saturn':300.}
BENEFICS={'Jupiter','Venus'}
MALEFICS={'Sun','Mars','Saturn'}

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


def _round(v):
    return round(float(v),4) if v is not None else None

def _aspect_strength(source, target):
    """BPHS-style full/partial graha drishti, linearly tapered around exact aspect."""
    name=source['name']
    sep=(target['longitude']-source['longitude'])%360
    if sep>180: sep=360-sep
    exact={7:180.0}
    if name=='Mars': exact.update({4:90.0,8:150.0})
    if name=='Jupiter': exact.update({5:120.0,9:120.0})
    if name=='Saturn': exact.update({3:60.0,10:90.0})
    # Treat each classical special aspect as a 30-degree influence window.
    distances=[abs(sep-a) for a in exact.values()]
    d=min(distances) if distances else 180
    return max(0.0,1.0-d/30.0)

def _ayana_bala(planet):
    # BPHS declination form: (23°27' +/- declination) scaled to 60.
    dec=planet.get('declination_deg')
    if dec is None: return None
    name=planet['name']
    if name in ('Moon','Saturn'): signed=-dec
    elif name=='Mercury': signed=abs(dec)
    else: signed=dec
    return max(0.0,min(60.0,(23.45+signed)/46.9*60.0)) * (2 if name=='Sun' else 1)

def shadbala(planets, varga_sign_fn=None, kala_context=None):
    lookup={p['name']:p for p in planets}
    asc=lookup['Ascendant']['longitude']
    kala_context=kala_context or {}
    rows=[]
    for name,natural in NATURAL.items():
        p=lookup[name]; longitude=p['longitude']
        uchcha=(180-shortest(longitude,EXALT[name]))/3
        # Dig Bala from actual angular cusps when supplied; fallback is explicitly labelled.
        best_points={'Sun':kala_context.get('mc_longitude'),
                     'Mars':kala_context.get('mc_longitude'),
                     'Moon':kala_context.get('ic_longitude'),
                     'Venus':kala_context.get('ic_longitude'),
                     'Mercury':asc,'Jupiter':asc,
                     'Saturn':kala_context.get('desc_longitude')}
        best=best_points[name]
        if best is None:
            best=(asc+30*(BEST_HOUSE[name]-1))%360
            dig_method='whole_sign_angular_proxy'
        else: dig_method='quadrant_cusp_longitude'
        dig=(180-shortest(longitude,best))/3
        sign=int(longitude//30)
        navamsha=int((longitude%30)//(30/9))
        nav_sign=(sign*9+navamsha)%12
        preference={'Sun':0,'Mars':0,'Jupiter':0,'Moon':1,'Venus':1,
                    'Mercury':0,'Saturn':0}
        target=preference[name]
        ojha=15*(int(sign%2==target)+int(nav_sign%2==target))
        house=int(p['house'])
        kendradi=60 if house in (1,4,7,10) else 30 if house in (2,5,8,11) else 15
        decanate=min(2,int((longitude%30)/10))
        preferred={'Sun':0,'Mars':0,'Jupiter':0,'Mercury':2,'Saturn':2,'Moon':1,'Venus':1}[name]
        drekkana=15 if decanate==preferred else 0
        varga_placements={}
        if varga_sign_fn:
            for division in SAPTAVARGA:
                mapped=int(longitude//30) if division==1 else varga_sign_fn(longitude,division)
                varga_placements[f'D{division}']={'sign_index':mapped,'sign_number':mapped+1,
                    'own_sign':mapped in OWN_SIGNS[name]}
        relationships={other:compound_relationship(name,other,lookup) for other in NATURAL_RELATIONS[name]}
        for entry in varga_placements.values():
            lord=SIGN_LORDS[entry['sign_index']]
            entry['sign_lord']=lord
            entry['compound_relationship_to_lord']='own' if lord==name else relationships[lord]
        saptavarga=score_saptavargaja(name,longitude,varga_placements) if varga_placements else None
        sthana_parts={'uchcha_bala':_round(uchcha),'saptavargaja_bala':saptavarga,
                      'ojhayugma_bala':_round(ojha),'kendradi_bala':_round(kendradi),
                      'drekkana_bala':_round(drekkana)}
        sthana=sum(v or 0 for v in sthana_parts.values())

        # Kala Bala. Time-of-day, paksha and hora/vara use the local sunrise context.
        elongation=(lookup['Moon']['longitude']-lookup['Sun']['longitude'])%360
        paksha_base=min(elongation,360-elongation)/3
        is_waxing=elongation<=180
        is_benefic_phase=is_waxing
        waxing_benefic={'Moon','Mercury','Jupiter','Venus'}
        paksha=paksha_base if ((name in waxing_benefic)==is_benefic_phase) else 60-paksha_base
        if name=='Moon': paksha=min(60,paksha*2)
        is_day=kala_context.get('is_daytime')
        sun_group_natonnata=kala_context.get('natonnata_sun_group')
        natonnata=(60.0 if name=='Mercury' else
                   sun_group_natonnata if name in ('Sun','Jupiter','Venus') else
                   (60.0-sun_group_natonnata) if sun_group_natonnata is not None else None) if is_day is not None else None
        tribhaga_index=kala_context.get('tribhaga_index')
        tribhaga_ruler=kala_context.get('tribhaga_ruler')
        tribhaga=60.0 if name=='Jupiter' else 60.0 if tribhaga_ruler==name else 0.0 if tribhaga_index else None
        vara_lord=kala_context.get('weekday_lord'); hora_lord=kala_context.get('hora_lord')
        vara=45.0 if vara_lord==name else 0.0 if vara_lord else None
        hora=60.0 if hora_lord==name else 0.0 if hora_lord else None
        abda_lord=kala_context.get('abda_lord'); masa_lord=kala_context.get('masa_lord')
        abda=15.0 if abda_lord==name else 0.0 if abda_lord else None
        masa=30.0 if masa_lord==name else 0.0 if masa_lord else None
        ayana=_ayana_bala(p)
        # Yuddha Bala only when two visible planets are within 1 degree; outcome needs
        # apparent-diameter/latitude comparison, so report candidate without inventing winner.
        wars=[]
        for other in ('Mars','Mercury','Jupiter','Venus','Saturn'):
            if other==name: continue
            sep=shortest(longitude,lookup[other]['longitude'])
            if sep<1.0: wars.append({'planet':other,'separation_deg':_round(sep),'status':'candidate_winner_requires_latitude_diameter_rule'})
        yuddha=0.0 if not wars else None
        kala_parts={'natonnata_bala':_round(natonnata),'paksha_bala':_round(paksha),
                    'tribhaga_bala':_round(tribhaga),'abda_bala':_round(abda),
                    'masa_bala':_round(masa),'vara_bala':_round(vara),'hora_bala':_round(hora),
                    'ayana_bala':_round(ayana),'yuddha_bala':_round(yuddha),
                    'yuddha_candidates':wars,'time_diagnostics':kala_context}
        kala_values=[natonnata,paksha,tribhaga,abda,masa,vara,hora,ayana,yuddha]
        kala=sum(v for v in kala_values if v is not None) if all(v is not None for v in kala_values) else None

        # Cheshta: Sun uses Ayana, Moon uses Paksha. For Mars-Saturn, classify
        # retrograde as full; direct speed is normalized against planet-specific mean speed.
        speed=p.get('longitude_speed_deg_per_day')
        if name=='Sun': cheshta=ayana
        elif name=='Moon': cheshta=paksha
        elif speed is None: cheshta=None
        elif speed<0: cheshta=60.0
        else:
            mean={'Mars':0.524,'Mercury':1.383,'Jupiter':0.083,'Venus':1.176,'Saturn':0.034}[name]
            ratio=max(0.0,min(1.0,speed/mean))
            cheshta=60.0*(1.0-ratio)
        cheshta_parts={'method':'BPHS motional cycle proxy; retrograde=60; direct speed normalized to mean daily motion',
                       'longitude_speed_deg_per_day':speed,'retrograde':p.get('retrograde')}

        # Drik Bala: benefic aspects add, malefic aspects subtract; 1/4 aspect pinda.
        benefic_total=0.0; malefic_total=0.0; aspect_rows=[]
        for other in NATURAL:
            if other==name: continue
            source=lookup[other]; strength=_aspect_strength(source,p)
            if strength<=0: continue
            # Quarter aspect pinda; Jupiter/Mercury receive the full value per BPHS note.
            weight=60.0*strength*(1.0 if other in ('Jupiter','Mercury') else 0.25)
            if other in BENEFICS: benefic_total+=weight
            elif other in MALEFICS: malefic_total+=weight
            else: benefic_total+=weight*0.5
            aspect_rows.append({'from':other,'aspect_fraction':_round(strength),'weighted_virupas':_round(weight)})
        drik=benefic_total-malefic_total
        components={'sthana_bala':_round(sthana),'dig_bala':_round(dig),'kala_bala':_round(kala),
                    'cheshta_bala':_round(cheshta),'naisargika_bala':_round(natural),'drik_bala':_round(drik)}
        # Total only when every six bala categories are numerically complete.
        complete=all(v is not None for v in components.values())
        total=sum(components.values()) if complete else None
        minimum=MINIMUM_VIRUPAS[name]
        rows.append({'name':name,'components':components,'sthana_subcomponents':sthana_parts,
            'kala_subcomponents':kala_parts,'cheshta_diagnostics':cheshta_parts,
            'drik_diagnostics':{'benefic_aspect_virupas':_round(benefic_total),
                'malefic_aspect_virupas':_round(malefic_total),'aspects_received':aspect_rows,
                'method':'orb-weighted Parashari graha drishti approximation'},
            'saptavargaja_diagnostics':{'planetary_relationships':relationships,'placements':varga_placements,
                'own_sign_count':sum(v['own_sign'] for v in varga_placements.values()),
                'bala_virupas':saptavarga,'status':'scored_convention_pending_external_validation' if saptavarga is not None else 'unavailable'},
            'motion_diagnostics':{'longitude_speed_deg_per_day':speed,'retrograde':p.get('retrograde')},
            'total_virupas':_round(total),'total_rupas':_round(total/60) if total is not None else None,
            'minimum_required_virupas':minimum,'minimum_required_rupas':minimum/60,
            'strength_ratio':_round(total/minimum) if total is not None else None,
            'meets_minimum':bool(total>=minimum) if total is not None else None})
    full=all(r['total_virupas'] is not None for r in rows)
    return {'status':'provisional_calculated' if full else 'provisional_components_with_gaps',
        'unit':'virupa','rupas_per_rupa':60,
        'methodology':'Classical BPHS component structure with declared computational conventions. Saptavargaja uses the project Raman-style point schedule; Abda/Masa use Gregorian year/month weekday proxies; Cheshta direct-motion and Drik aspect-orb methods are approximations. Yuddha Bala is withheld when a war candidate needs winner determination. Validate against independent reference charts before predictive use.',
        'limitations':['Abda/Masa lords use calendar weekday proxies, not the full Ahargana method.',
            'Cheshta Bala uses a speed-normalized approximation for direct motion; retrograde receives 60 virupas.',
            'Drik Bala uses orb-weighted Parashari aspect approximations, not a complete BPHS Drishti Pinda implementation.',
            'Yuddha Bala is zero when no close conjunction candidate exists; winner/loser adjustment is withheld for candidates.',
            'Dig Bala uses quadrant cusps only if supplied; otherwise whole-sign angular proxy.'],
        'planets':rows}
