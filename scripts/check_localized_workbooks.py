"""Check localized workbook structure against the English content source."""
from pathlib import Path
from collections import Counter
import re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'mcp-weather-2hour-v1/workbook'

def blocks(s):return re.findall(r'```[\s\S]*?```',s)
def identifiers(s):return Counter(re.findall(r'(?<!`)`([^`\n]+)`(?!`)',s))
def links(s):return re.findall(r'\]\((https?[^)]+)\)',s)
def tables(s):
    result=[]
    for m in re.finditer(r'(?:^\|.*\n)+',s,re.M):
        rows=[r for r in m.group().splitlines() if not re.fullmatch(r'\|[\s:|\-]+\|',r)]
        result.append([len(r.strip('|').split('|')) for r in rows])
    return result

def main():
    en=(BASE/'MCP_Colab_Student_Workbook.md').read_text()
    for lang,suffix,label in [('ja','JA','手順'),('zh-CN','ZH_CN','步骤')]:
        path=BASE/lang/f'MCP_Colab_Student_Workbook_{suffix}.md';s=path.read_text()
        assert list(map(int,re.findall(r'^### '+label+r'(\d+)\.',s,re.M)))==list(range(1,39)),path
        assert list(map(int,re.findall(r'^## (\d+)\.',s,re.M)))==list(range(1,12)),path
        assert blocks(s)==blocks(en),f'Code/output block drift: {path}'
        assert identifiers(s)==identifiers(en),f'Technical identifier drift: {path}'
        assert links(s)==links(en),f'Link drift: {path}'
        assert tables(s)==tables(en),f'Table structure drift: {path}'
        assert s.count('<!-- pagebreak -->')==11,path
        assert s.count('- [ ]')==en.count('- [ ]'),path
        assert 'Rajkumar Rajagobalan' in s,path
        print(f'{lang}: all 38 steps; 11 sections; code, identifiers, links, tables and checklist preserved.')
if __name__=='__main__':main()
