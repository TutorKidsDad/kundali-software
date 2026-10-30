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
        components={key:None for key in COMPONENTS}
        components['dig_bala']=round(dig,4)
        components['naisargika_bala']=round(natural,4)
        rows.append({'name':name,'components':components,
                     'sthana_subcomponents':{'uchcha_bala':round(uchcha,4)},
                     'calculated_partial_virupas':round(dig+natural+uchcha,4),
                     'total_virupas':None,'total_rupas':None,'meets_minimum':None})
    return {'status':'partial_not_validated','unit':'virupa',
            'note':'Dig Bala and Naisargika Bala are calculated; Uchcha Bala is only one part of Sthana Bala. Kala, Cheshta, Drik and remaining Sthana subcomponents are pending. Partial subtotal is NOT a Shadbala total. Dig uses whole-sign angular offsets from Lagna, not measured quadrant cusps.',
            'planets':rows}
