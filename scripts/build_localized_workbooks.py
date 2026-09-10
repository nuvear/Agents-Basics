"""Build Japanese and Simplified Chinese student PDFs from localized Markdown.

Dependencies: reportlab, fonttools. Noto Sans JP/SC (SIL OFL) variable fonts
are downloaded from the Google Fonts repository into a private build cache.
Set WORKBOOK_FONT_DIR to a DejaVu font folder for code; otherwise the builder
tries the usual Linux path. Pass --language ja or zh-CN, or omit for both.
"""
from pathlib import Path
import argparse, os, re, html, urllib.request
from fontTools.ttLib import TTFont as FontToolsFont
from fontTools.varLib.instancer import instantiateVariableFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import reportlab.lib.textsplit as textsplit
import reportlab.platypus.paragraph as paragraph_module
# Include Chinese full-width punctuation in the line-start prohibition.
for module in (textsplit, paragraph_module):
    module.ALL_CANNOT_START += "，；：！？）》〉】”’"

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.course-build/fonts'
EDITIONS={
 'ja':('JP','JA','天気情報エージェントとMCP - 受講者用ワークブック','受講者用ワークブック | 日本語版 v1.0'),
 'zh-CN':('SC','ZH_CN','天气智能体与MCP - 学员实训手册','学员实训手册 | 简体中文版 v1.0'),
}

def font_for(region,weight):
    CACHE.mkdir(parents=True,exist_ok=True)
    stem='NotoSans'+region
    variable=CACHE/(stem+'-Variable.ttf')
    if not variable.exists():
        url='https://raw.githubusercontent.com/google/fonts/main/ofl/'+stem.lower()+'/'+stem+'%5Bwght%5D.ttf'
        urllib.request.urlretrieve(url,variable)
    static=CACHE/(stem+'-'+str(weight)+'.ttf')
    if not static.exists():
        font=FontToolsFont(variable)
        instantiateVariableFont(font,{'wght':weight},inplace=True).save(static)
    return static

def build(language):
    region,suffix,title,header=EDITIONS[language]
    source=ROOT/f'mcp-weather-2hour-v1/workbook/{language}/MCP_Colab_Student_Workbook_{suffix}.md'
    output=ROOT/f'output/pdf/MCP_Colab_Student_Workbook_{suffix}.pdf'
    body='Body'+region;bold=body+'Bold';mono='Mono'
    for name,weight in [(body,400),(bold,700)]:
        pdfmetrics.registerFont(TTFont(name,str(font_for(region,weight))))
    fontdir=Path(os.environ.get('WORKBOOK_FONT_DIR','/usr/share/fonts/truetype/dejavu'))
    pdfmetrics.registerFont(TTFont(mono,str(fontdir/'DejaVuSansMono.ttf')))
    pdfmetrics.registerFontFamily(body,normal=body,bold=bold,italic=body,boldItalic=bold)
    navy=colors.HexColor('#17334A');teal=colors.HexColor('#007E87');ink=colors.HexColor('#263747');muted=colors.HexColor('#667582')
    styles={
     'body':ParagraphStyle('body',fontName=body,fontSize=9.6,leading=14.3,textColor=ink,spaceAfter=7,wordWrap='CJK'),
     'h1':ParagraphStyle('h1',fontName=bold,fontSize=27,leading=35,textColor=navy,spaceBefore=20,spaceAfter=16,wordWrap='CJK'),
     'h2':ParagraphStyle('h2',fontName=bold,fontSize=17,leading=23,textColor=navy,spaceAfter=12,wordWrap='CJK',keepWithNext=True),
     'h3':ParagraphStyle('h3',fontName=bold,fontSize=11,leading=15,textColor=teal,spaceBefore=9,spaceAfter=5,wordWrap='CJK',keepWithNext=True),
     'table':ParagraphStyle('table',fontName=body,fontSize=8.5,leading=12,textColor=ink,wordWrap='CJK'),
     'code':ParagraphStyle('code',fontName=mono,fontSize=8,leading=11,textColor=navy,backColor=colors.HexColor('#F0F4F7'),borderPadding=8,spaceBefore=4,spaceAfter=10),
     'callout':ParagraphStyle('callout',fontName=body,fontSize=9,leading=13.3,textColor=navy,backColor=colors.HexColor('#EAF5F4'),borderPadding=9,spaceBefore=6,spaceAfter=11,wordWrap='CJK'),
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
        n=len(rows[0]);widths=([156,327] if n==2 else [153,165,165])
        data=[[Paragraph(('<b>'+inline(c)+'</b>') if i==0 else inline(c),styles['table']) for c in row] for i,row in enumerate(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDEBED')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),0.7,teal),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#D6DEE3')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FA')])]))
        return [t,Spacer(1,9)]
    story=[];lines=source.read_text().splitlines();i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line=='<!-- pagebreak -->':story.append(PageBreak());i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
            for row in block:
                if pdfmetrics.stringWidth(row,mono,8)>467:raise ValueError('Code exceeds printable width: '+row)
            story.append(Preformatted('\n'.join(block),styles['code']));i+=1;continue
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
        canvas.setTitle(title);canvas.setAuthor('Rajkumar Rajagobalan')
        canvas.setSubject('Draft v1.0 | '+language+' | Google Colab two-hour workshop')
        canvas.setFillColor(teal);canvas.rect(0,h-9,w,9,fill=1,stroke=0)
        canvas.setFont(body,8);canvas.setFillColor(muted)
        canvas.drawString(56,h-34,'AGENTS BASICS / GOOGLE COLAB')
        canvas.drawRightString(w-56,h-34,header)
        canvas.setStrokeColor(colors.HexColor('#D6DEE3'));canvas.line(56,43,w-56,43)
        canvas.setFont(body,7.6);canvas.drawString(56,29,'Rajkumar Rajagobalan')
        canvas.drawRightString(w-56,29,f'{doc.page:02d}')
    output.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(output),pagesize=A4,rightMargin=56,leftMargin=56,topMargin=58,bottomMargin=59).build(story,onFirstPage=page,onLaterPages=page)
    print(output,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--language',choices=EDITIONS)
    args=parser.parse_args()
    for language in ([args.language] if args.language else EDITIONS):build(language)
