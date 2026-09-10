"""Render the student workbook Markdown as a paginated, linked PDF.

Requires reportlab. Set WORKBOOK_FONT_DIR to a directory of DejaVu Sans fonts,
or use a standard Linux font installation. The Markdown is the content source.
"""
from pathlib import Path
import os,re,html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'mcp-weather-2hour-v1/workbook/MCP_Colab_Student_Workbook.md'
OUTPUT=ROOT/'output/pdf/MCP_Colab_Student_Workbook.pdf'
fontdir=Path(os.environ.get('WORKBOOK_FONT_DIR','/usr/share/fonts/truetype/dejavu'))
for name,file in [('Body','DejaVuSans.ttf'),('BodyBold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
navy=colors.HexColor('#17334A'); teal=colors.HexColor('#007E87'); ink=colors.HexColor('#263747'); muted=colors.HexColor('#667582')
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9.6,leading=14.3,textColor=ink,spaceAfter=7),
 'h1':ParagraphStyle('h1',fontName='BodyBold',fontSize=29,leading=35,textColor=navy,spaceBefore=20,spaceAfter=16),
 'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=18,leading=23,textColor=navy,spaceAfter=12),
 'h3':ParagraphStyle('h3',fontName='BodyBold',fontSize=11,leading=15,textColor=teal,spaceBefore=9,spaceAfter=5,keepWithNext=True),
 'table':ParagraphStyle('table',fontName='Body',fontSize=8.5,leading=12,textColor=ink),
 'code':ParagraphStyle('code',fontName='Mono',fontSize=8,leading=11,textColor=navy,backColor=colors.HexColor('#F0F4F7'),borderPadding=8,spaceBefore=4,spaceAfter=10),
 'callout':ParagraphStyle('callout',fontName='Body',fontSize=9,leading=13.3,textColor=navy,backColor=colors.HexColor('#EAF5F4'),borderPadding=9,spaceBefore=6,spaceAfter=11),
}
def inline(text):
    tokens=[]
    def link(m):
        tokens.append('<link href="'+html.escape(m.group(2),quote=True)+'" color="#007E87"><u>'+html.escape(m.group(1))+'</u></link>')
        return f'ZZLINK{len(tokens)-1}ZZ'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
    text=html.escape(text)
    text=re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    for i,token in enumerate(tokens):text=text.replace(f'ZZLINK{i}ZZ',token)
    return text

def para(text,kind='body'):return Paragraph(inline(text),styles[kind])

def table(lines):
    rows=[[cell.strip() for cell in row.strip().strip('|').split('|')] for row in lines]
    rows=[row for row in rows if not all(re.fullmatch(r':?-+:?',c) for c in row)]
    n=len(rows[0]); widths=([156,327] if n==2 else [153,165,165])
    data=[[Paragraph(('<b>'+inline(c)+'</b>') if i==0 else inline(c),styles['table']) for c in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDEBED')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),0.7,teal),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#D6DEE3')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FA')])]))
    return [t,Spacer(1,9)]

story=[]
lines=SOURCE.read_text().splitlines();i=0
while i<len(lines):
    line=lines[i]
    if not line.strip():i+=1;continue
    if line=='<!-- pagebreak -->':story.append(PageBreak());i+=1;continue
    if line.startswith('```'):
        block=[];i+=1
        while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
        # Wrap only overly long code at commas; preserve executable formatting.
        rendered=[]
        for row in block:
            if pdfmetrics.stringWidth(row,'Mono',8)>467:
                raise ValueError('Code line exceeds printable width: '+row)
            rendered.append(row)
        story.append(Preformatted('\n'.join(rendered),styles['code']));i+=1;continue
    if line.startswith('|'):
        block=[]
        while i<len(lines) and lines[i].startswith('|'):block.append(lines[i]);i+=1
        story.extend(table(block));continue
    if line.startswith('# '):story.append(para(line[2:],'h1'))
    elif line.startswith('## '):story.append(para(line[3:],'h2'))
    elif line.startswith('### '):story.append(para(line[4:],'h3'))
    elif line.startswith('> '):story.append(para(line[2:],'callout'))
    elif line.startswith('- '):story.append(para('• '+line[2:]))
    else:story.append(para(line))
    i+=1

def page(canvas,doc):
    w,h=A4
    canvas.setTitle('Weather Agents and MCP - Step-by-step student workbook')
    canvas.setAuthor('Rajkumar Rajagobalan')
    canvas.setSubject('Draft v1.0 - Two-hour Google Colab workshop')
    canvas.setFillColor(teal);canvas.rect(0,h-9,w,9,fill=1,stroke=0)
    canvas.setFont('Body',8);canvas.setFillColor(muted)
    canvas.drawString(56,h-34,'AGENTS BASICS  /  GOOGLE COLAB')
    canvas.drawRightString(w-56,h-34,'STUDENT WORKBOOK  •  DRAFT v1.0')
    canvas.setStrokeColor(colors.HexColor('#D6DEE3'));canvas.line(56,43,w-56,43)
    canvas.setFont('Body',7.6);canvas.drawString(56,29,'Rajkumar Rajagobalan')
    canvas.drawRightString(w-56,29,f'{doc.page:02d}')

OUTPUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=56,leftMargin=56,topMargin=58,bottomMargin=59)
doc.build(story,onFirstPage=page,onLaterPages=page)
print(OUTPUT)
