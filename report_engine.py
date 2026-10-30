"""Complete data report from an existing /api/chart result; avoids browser screenshot truncation."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.lib.colors import HexColor


PLANET_SHORT = {'Ascendant':'Asc','Sun':'Su','Moon':'Mo','Mars':'Ma','Mercury':'Me',
                'Jupiter':'Ju','Venus':'Ve','Saturn':'Sa','Rahu':'Ra','Ketu':'Ke'}

def north_indian_chart(planets, size=300):
    """North Indian fixed-house layout: 1 at top, 4 left, 7 bottom, 10 right."""
    d = Drawing(size, size)
    edge = HexColor('#34465c')
    d.add(Rect(0,0,size,size,strokeColor=edge,strokeWidth=1.4,fillColor=None))
    half=size/2
    # Side-midpoint diamond and both corner-to-corner diagonals.
    for a,b,c,e in [(half,size,0,half),(0,half,half,0),(half,0,size,half),(size,half,half,size),
                    (0,0,size,size),(0,size,size,0)]:
        d.add(Line(a,b,c,e,strokeColor=edge,strokeWidth=1.05))
    # House number positions and planet label positions. The houses, not signs,
    # are fixed in a North Indian chart.
    centers={1:(.50,.79),2:(.24,.88),3:(.12,.73),4:(.23,.50),
             5:(.12,.27),6:(.25,.12),7:(.50,.23),8:(.75,.12),
             9:(.88,.27),10:(.77,.50),11:(.88,.73),12:(.75,.88)}
    by_house={h:[] for h in range(1,13)}
    for p in planets:
        h=p.get('house')
        if h in by_house:
            by_house[h].append(PLANET_SHORT.get(p.get('name'),str(p.get('name',''))[:3]))
    asc=next((p.get('sign_index') for p in planets if p.get('name')=='Ascendant'),0)
    for house,(cx,cy) in centers.items():
        x,y=cx*size,cy*size
        sign_number=((asc+house-1)%12)+1
        d.add(String(x,y+10,str(sign_number),textAnchor='middle',fontName='Helvetica-Bold',
                     fontSize=10,fillColor=HexColor('#284a76')))
        names=by_house[house]
        # Wrap planet abbreviations to keep text within narrow triangles.
        for i in range(0,len(names),3):
            d.add(String(x,y-3-11*(i//3),' '.join(names[i:i+3]),textAnchor='middle',
                         fontName='Helvetica',fontSize=8,fillColor=HexColor('#252525')))
    return d

def build_report(data):
    out=BytesIO()
    doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=34,rightMargin=34,topMargin=35,bottomMargin=35)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle',parent=styles['Title'],fontSize=18,spaceAfter=14))
    styles.add(ParagraphStyle(name='ReportSmall',parent=styles['Normal'],fontSize=8,leading=11))
    story=[]
    def para(value): return Paragraph(escape(str(value)),styles['ReportSmall'])
    def heading(s):story.append(Spacer(1,12));story.append(Paragraph(escape(s),styles['Heading2']))
    def table(headers, rows):
        values=[[para(v) for v in headers]]+[[para(v) for v in row] for row in rows]
        t=Table(values,repeatRows=1,hAlign='LEFT',colWidths=None)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf6')),('GRID',(0,0),(-1,-1),.3,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.append(t)
    story.append(Paragraph('Kundli Explorer - Complete Calculation Report',styles['ReportTitle']))
    for key in ('name','place','date_of_birth','time_of_birth','timezone','latitude','longitude','local_time','utc_time','ascendant_sign','ayanamsha','nodes','house_system','ephemeris'):
        story.append(para(f'{key.replace("_"," ").title()}: {data.get(key,"-")}'))
    heading('D1 - Rashi / Lagna Chart (North Indian Style)')
    story.append(north_indian_chart(data.get('planets',[])))
    story.append(para('Blue numbers indicate zodiac signs (1 = Aries); planet abbreviations appear in their houses.'))
    heading('D1 Planetary Positions')
    table(['Planet','Sign','Degree','House','Nakshatra','Pada'],[[p.get('name'),p.get('sign'),p.get('degree'),p.get('house'),p.get('nakshatra'),p.get('pada')] for p in data.get('planets',[])])
    for key,v in data.get('vargas',{}).items():
        story.append(PageBreak())
        heading(f'{key} Divisional Chart - Ascendant: {v.get("ascendant_sign", "-")}')
        story.append(north_indian_chart(v.get('planets',[])))
        table(['Planet','Sign','Degree','House'],[[p.get('name'),p.get('sign'),p.get('degree'),p.get('house')] for p in v.get('planets',[])])
    d=data.get('vimshottari',{})
    heading('Vimshottari Dasha')
    story.append(para('Birth Nakshatra: '+str(d.get('birth_nakshatra','-'))+'; Balance years: '+str(d.get('balance_at_birth_years','-'))))
    for md in d.get('mahadashas',[]):
        heading('Mahadasha: '+md['lord'])
        story.append(para(f"{md['start_utc']} to {md['end_utc']}"))
        table(['Antardasha','Start UTC','End UTC'],[[ad['lord'],ad['start_utc'][:10],ad['end_utc'][:10]] for ad in md.get('antardashas',[])])
        for ad in md.get('antardashas',[]):
            story.append(para('Pratyantardasha during '+md['lord']+' / '+ad['lord']))
            table(['Lord','Start UTC','End UTC'],[[pr['lord'],pr['start_utc'][:10],pr['end_utc'][:10]] for pr in ad.get('pratyantardashas',[])])
    a=data.get('analysis',{})
    heading('Graha Drishti')
    table(['Planet','Aspect','Target Sign','House'],[[p.get('planet'),p.get('offset'),p.get('target_sign'),p.get('target_house')] for p in a.get('graha_drishti',{}).get('aspects',[])])
    heading('Yoga Checks')
    for y in a.get('yoga_checks',{}).get('matches',[]):story.append(para(y.get('name','')+': '+y.get('rule','')))
    av=data.get('ashtakavarga',{})
    heading('Ashtakavarga')
    story.append(para('SAV total: '+str(av.get('total','-'))))
    table(['Graha']+[str(i) for i in range(1,13)],[[name]+vals for name,vals in av.get('bav',{}).items()]+[['SAV']+av.get('sav',[])])
    heading('Shadbala - Calculation Status')
    sh=data.get('shadbala',{})
    story.append(para(sh.get('note','Shadbala unavailable.')))
    table(['Planet','Uchcha*','Dig','Naisargika','Partial*','Full'],[[p['name'],p.get('sthana_subcomponents',{}).get('uchcha_bala','-'),p['components'].get('dig_bala','-'),p['components']['naisargika_bala'],p.get('calculated_partial_virupas','-'),'Pending'] for p in sh.get('planets',[])])
    story.append(Spacer(1,15));story.append(para('Calculated results are based on the application conventions; Shadbala is partial and must not be interpreted as a completed strength score.'))
    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(HexColor('#d7e0eb'))
        canvas.line(34,27,A4[0]-34,27)
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(HexColor('#526479'))
        canvas.drawString(34,17,'Kundli Explorer | Calculation report')
        canvas.drawRightString(A4[0]-34,17,f'Page {document.page}')
        canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
