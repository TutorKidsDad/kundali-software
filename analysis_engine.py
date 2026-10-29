"""Transparent D1 rule-based Jyotish diagnostics; not a Shadbala implementation."""
SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
GRAHAS = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
LORDS = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter']
EXALT = {'Sun':0,'Moon':1,'Mars':9,'Mercury':5,'Jupiter':3,'Venus':11,'Saturn':6}
OWN = {'Sun':[4],'Moon':[3],'Mars':[0,7],'Mercury':[2,5],'Jupiter':[8,11],'Venus':[1,6],'Saturn':[9,10]}
SPECIAL = {'Mars':[4,8], 'Jupiter':[5,9], 'Saturn':[3,10]}

def analyze(planets):
    byname={p['name']:p for p in planets}
    asc=byname['Ascendant']['sign_index']
    aspects=[]
    for name in GRAHAS:
        p=byname[name]
        offsets=sorted(set([7]+SPECIAL.get(name,[])))
        for offset in offsets:
            target=(p['sign_index']+offset-1)%12
            aspects.append({'planet':name,'from_sign':p['sign'],'offset':offset,
                'target_sign':SIGNS[target], 'target_house':(target-asc)%12+1,
                'occupants':[q['name'] for q in planets if q['name']!='Ascendant' and q['sign_index']==target]})
    yogas=[]
    def add(name,condition,explanation):
        if condition:yogas.append({'name':name,'rule':explanation,'status':'rule-match; interpretation not implied'})
    for name in GRAHAS:
        p=byname[name]
        add(f'{name} in own sign',p['sign_index'] in OWN[name],f'{name} occupies an own Rashi')
        add(f'{name} in exaltation sign',p['sign_index']==EXALT[name],f'{name} occupies its traditional exaltation Rashi; exact exaltation degree is not tested')
    for name,label in [('Mars','Ruchaka'),('Mercury','Bhadra'),('Jupiter','Hamsa'),('Venus','Malavya'),('Saturn','Shasha')]:
        p=byname[name]
        add(f'{label} (Pancha Mahapurusha) — basic sign/house test',p['house'] in [1,4,7,10] and (p['sign_index'] in OWN[name] or p['sign_index']==EXALT[name]),f'{name} in a Kendra (1/4/7/10) and own or exaltation sign; combustion, strength and exceptions not assessed')
    moon=byname['Moon']; jupiter=byname['Jupiter']
    relative=(jupiter['sign_index']-moon['sign_index'])%12+1
    add('Gaja Kesari — basic Moon/Jupiter Kendra test',relative in (1,4,7,10),'Jupiter in a Kendra from the Moon; cancellation and planetary strength not assessed')
    return {'graha_drishti':{'method':'Parashari whole-sign graha drishti; 7th for all seven classical planets, additional Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th','aspects':aspects,'nodes_excluded':True},
        'yoga_checks':{'method':'Selected preliminary D1 sign-and-house rules only','matches':yogas,'limitations':'Not a comprehensive Yoga assessment. Does not account for combustion, planetary war, orb, cancellation, functional beneficence, or strength.'},
        'ashtakavarga':{'status':'not_implemented','reason':'Bhinna/Sarvashtakavarga require separately validated classical contributor rules; no fabricated scores are shown'},
        'shadbala':{'status':'not_implemented','reason':'Sixfold strength requires validated positional, directional, temporal, motional, natural and aspect strength algorithms; no fabricated values are shown'}}
