from pathlib import Path
import ast,re,json,time,concurrent.futures
from html.parser import HTMLParser
from urllib.parse import urlencode
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent.parent
ZH=re.compile(r'[\u3400-\u9fff]')
Q=re.compile(r"""(['"])((?:\\.|(?!\1)[^\\])*?)\1""",re.S)
B=re.compile(chr(96)+r'((?:\\.|[^\\])*?)'+chr(96),re.S)
T=re.compile(r'\$\{[^{}]*\}')
J=re.compile(r'>\s*([^<>{}\n]{1,220})\s*<')
def clean(s):
 s=s.strip()
 if not(1<=len(s)<=230 and ZH.search(s)) or any(x in s for x in ('\n','\r','<script','</','=>','<div','<span')):return None
 if s.startswith(('//','/*','<','const ','import ','function ','export ','return ','if ')):return None
 if len(s)>12 and(s.count('(')>2 or s.count(';')>2 or s.count('{')>3):return None
 return s
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.values=set();self.skip=0
 def handle_starttag(self,t,attrs):
  if t in ('script','style','svg'):self.skip+=1
  if not self.skip:
   for k,v in attrs:
    if k in ('title','aria-label','placeholder','aria-placeholder'):
     x=clean(v or '')
     if x:self.values.add(x)
 def handle_endtag(self,t):
  if t in ('script','style','svg') and self.skip:self.skip-=1
 def handle_data(self,v):
  if not self.skip:
   x=clean(v)
   if x:self.values.add(x)
def inventory():
 out={}
 def add(x,p):
  if x:out.setdefault(x,set()).add(str(p))
 for p in (ROOT/'frontend/src').rglob('*'):
  if p.suffix not in ('.ts','.tsx','.js','.html'):continue
  s=p.read_text('utf8',errors='replace')
  s=re.sub(r'/\*[\s\S]*?\*/','',s)
  s=re.sub(r'^\s*//[^\n]*','',s,flags=re.M)
  for m in Q.finditer(s):add(clean(m.group(2)),p.relative_to(ROOT))
  for m in B.finditer(s):
   x=m.group(1)
   if '$'+'{' in x:
    n=[0]
    def repl(_):
     i=n[0];n[0]+=1;return '{'+str(i)+'}'
    x=T.sub(repl,x)
   add(clean(x),p.relative_to(ROOT))
  for m in J.finditer(s):add(clean(m.group(1)),p.relative_to(ROOT))
 pyfiles=list((ROOT/'src/peach').glob('routes_*.py'))
 pyfiles += [ROOT/'src/peach'/x for x in ('onboarding.py','web_entry.py','api.py','auth.py')]
 for p in pyfiles:
  if not p.is_file():continue
  try:tree=ast.parse(p.read_text('utf8'))
  except SyntaxError:continue
  for node in ast.walk(tree):
   if isinstance(node,ast.Constant) and isinstance(node.value,str):add(clean(node.value),p.relative_to(ROOT))
   if isinstance(node,ast.JoinedStr):
    parts=[];n=0
    for v in node.values:
     if isinstance(v,ast.Constant):parts.append(str(v.value))
     elif isinstance(v,ast.FormattedValue):parts.append('{'+str(n)+'}');n+=1
    add(clean(''.join(parts)),p.relative_to(ROOT))
 p=HTML();p.feed((ROOT/'web/index.html').read_text('utf8'))
 for x in p.values:add(x,'web/index.html')
 return out
SEP='\n⟦PEACHUISEP⟧\n'
def translate(q):
 url='https://translate.googleapis.com/translate_a/single?'+urlencode({'client':'gtx','sl':'zh-CN','tl':'en','dt':'t','q':q})
 req=Request(url,headers={'User-Agent':'Mozilla/5.0'})
 for a in range(3):
  try:
   with urlopen(req,timeout=23) as r:data=json.load(r)
   return ''.join(x[0] or '' for x in data[0]).strip()
  except Exception:
   if a==2:raise
   time.sleep(1+a*2)
def good(s,t):
 return bool(t and len(t)<=600 and not ZH.search(t) and set(re.findall(r'\{\d+\}',s)).issubset(set(re.findall(r'\{\d+\}',t))))
def batch(g):
 result={};failed=[]
 try:
  tr=translate(SEP.join(g))
  parts=re.split(r'\s*⟦PEACHUISEP⟧\s*',tr)
  if len(parts)==len(g):
   for s,t in zip(g,parts):
    if good(s,t.strip()):result[s]=t.strip()
 except Exception:pass
 for s in g:
  if s in result:continue
  try:
   t=translate(s)
   if good(s,t):result[s]=t
   else:failed.append(s)
  except Exception:failed.append(s)
 return result,failed
def main():
 catalog=json.loads((ROOT/'web/peach-ui-en.json').read_text('utf8'))
 src=inventory();todo=sorted((x for x in src if x not in catalog),key=lambda x:(len(x),x))
 groups=[todo[i:i+12] for i in range(0,len(todo),12)]
 print('Source strings:',len(src),'Curated:',len(set(src)&set(catalog)),'Untranslated:',len(todo),'Groups:',len(groups),flush=True)
 translated={};missing=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
  pending=[executor.submit(batch,g) for g in groups]
  for i,f in enumerate(concurrent.futures.as_completed(pending),1):
   a,b=f.result();translated.update(a);missing+=b
   if i%20==0:print('Progress',i,'/',len(groups),'translated',len(translated),'failed',len(missing),flush=True)
 out=Path('english-audit-output');out.mkdir(exist_ok=True)
 (out/'translations.json').write_text(json.dumps({**catalog,**translated},ensure_ascii=False,indent=2)+'\n','utf8')
 (out/'coverage.json').write_text(json.dumps({'source_candidates':len(src),'curated_covered':len(set(src)&set(catalog)),'machine_translated':len(translated),'untranslated':len(missing),'untranslated_examples':missing[:150],'machine_translation_warning':'Not human-reviewed; candidate strings include non-visible copy; metadata must be excluded at runtime.'},ensure_ascii=False,indent=2),'utf8')
 (out/'sources.json').write_text(json.dumps({k:sorted(v) for k,v in src.items()},ensure_ascii=False,indent=2),'utf8')
 print('FINAL',len(src),len(translated),len(missing),flush=True)
if __name__=='__main__':main()
