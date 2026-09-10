import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(import.meta.dirname,'..');
const SKILL=process.env.PRESENTATIONS_SKILL_DIR;
if(!SKILL) throw new Error('Set PRESENTATIONS_SKILL_DIR to the Codex presentations skill directory.');
const PY=process.env.PYTHON_EXECUTABLE || 'python3';
const {finalizePresentation,resolvePresentationFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const FONT=resolvePresentationFont({fontFamily:'DejaVu Sans'});
const MONO=resolvePresentationFont({fontFamily:'DejaVu Sans Mono'});
const C={navy:'#17334A',teal:'#007E87',ink:'#263747',muted:'#667582',light:'#EEF5F5',white:'#FFFFFF',amber:'#E1A642'};
const data=JSON.parse(await fs.readFile(path.join(ROOT,'teaching/slides.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
function txt(s,text,x,y,w,h,size=28,color=C.ink,bold=false,font=FONT){
 const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=text;t.text.style={typeface:font,fontSize:size,color,bold,autoFit:'none',insets:{left:0,right:0,top:0,bottom:0}};return t;
}
function link(s,label,uri,x,y,w=800,color=C.teal){const t=txt(s,'',x,y,w,42,26,color);t.text=[{run:label,link:{uri,isExternal:true},textStyle:{color,underline:'sng'}}];}
const tableOwners=[];
for(const d of data){
 const s=p.slides.add();const dark=['cover','break','close'].includes(d.layout);s.background.fill=dark?C.navy:C.white;
 const fg=dark?C.white:C.navy;
 txt(s,d.time+(d.minutes?' min · '+d.minutes+' min':''),64,678,750,25,18,dark?'#A8C8CD':C.muted);
 txt(s,String(d.number).padStart(2,'0'),1152,678,64,25,18,dark?'#A8C8CD':C.muted);
 if(d.layout==='cover'){
  txt(s,d.title,80,185,1100,100,68,C.white,true);
  txt(s,d.items[0],84,320,1090,60,33,'#B8DCDF');
  txt(s,d.items[1],84,451,950,55,30,C.white);
  txt(s,d.items[2],84,516,950,40,23,'#B8DCDF');
 }else if(d.layout==='break'){
  txt(s,d.title,80,190,1120,100,70,C.white,true);
  txt(s,d.items[0],84,335,1080,80,45,'#B8DCDF');
  txt(s,d.items[1],84,470,1050,90,30,C.white);
 }else if(d.layout==='close'){
  txt(s,d.title,64,54,1160,100,44,fg,true);
  d.items.forEach((v,i)=>txt(s,v,80,218+i*105,1100,75,44,C.white,i===0));
  link(s,'Repository and student materials',d.link,84,575,1000,'#B8DCDF');
 }else{
  txt(s,d.title,64,48,1152,86,44,fg,true);
  if(d.layout==='image'){
   s.images.add({blob:new Uint8Array(await fs.readFile(path.join(ROOT,'teaching/assets',d.image+'.png'))),contentType:'image/png',alt:d.title+' concept illustration',fit:'contain',position:{left:64,top:132,width:1152,height:470}});
   txt(s,d.items[0],64,607,1152,35,27,C.navy,true);
   txt(s,d.items[1],64,642,1152,32,23,C.ink);
  }else if(d.layout==='table'){
   const values=d.items;const rows=values.length,columns=values[0].length;
   const heights=rows>7?440:rows===6?400:rows===5?380:360;
   const t=s.tables.add({rows,columns,left:64,top:164,width:1152,height:heights,values,columnWidths:columns===2?[300,852]:columns===3?[320,416,416]:[300,284,284,284]});
   t.borders.assign({fill:'#D7E3E6',width:0.6,style:'solid'});
   for(let r=0;r<rows;r++)for(let c=0;c<columns;c++){
    const cell=t.getCell(r,c);cell.fill=r===0?C.navy:(r%2?C.white:C.light);
    cell.text.style={typeface:FONT,fontSize:columns===4?24:26,color:r===0?C.white:C.ink,bold:r===0,autoFit:'none',insets:{left:14,right:14,top:9,bottom:9}};
   }
   tableOwners.push(d.number);
  }else if(d.layout==='lab'){
   txt(s,d.workbook,64,148,1152,40,25,C.teal,true);
   d.items.forEach((v,i)=>txt(s,String(i+1)+'.  '+v,64,216+i*70,1152,60,30,C.ink));
   txt(s,d.code.replaceAll('\\n','\n'),64,533,1152,112,23,C.navy,false,MONO);
  }else if(d.layout==='columns'){
   d.items.forEach((v,i)=>{const lines=v.split('\n');const x=64+i*596;
    txt(s,lines[0],x,175,545,60,30,C.teal,true);
    lines.slice(1).forEach((line,j)=>txt(s,line,x,272+j*94,545,85,29,C.ink));
   });
  }else if(d.layout==='code'){
   d.items.forEach((v,i)=>txt(s,v,64,209+i*79,1152,74,27,C.navy,false,MONO));
   txt(s,d.caption||'',64,580,1152,58,24,C.teal);
  }else if(d.layout==='question'){
   d.items.forEach((v,i)=>txt(s,v,64,202+i*99,1152,78,35,C.ink));
  }else{
   const gap=d.items.length===5?84:99;
   d.items.forEach((v,i)=>txt(s,v,64,189+i*gap,1152,76,32,C.ink));
   if(d.link)link(s,'Open the Colab notebook',d.link,64,605);
  }
 }
 s.speakerNotes.textFrame.setText(d.notes);
}
const build=path.join(ROOT,'.deck-build');
await fs.mkdir(path.join(build,'previews'),{recursive:true});
const candidate=path.join(build,'candidate.pptx');
await(await PresentationFile.exportPptx(p)).save(candidate);
console.log('Exported draft',candidate);
for(let i=0;i<data.length;i++){
 const slide=p.slides.items[i];
 const png=await p.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(build,'previews',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 console.log('Rendered',i+1);
}
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:path.join(ROOT,'output/pptx/MCP_Weather_Teaching_Deck.pptx'),pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tableOwners,fontPolicy:{basis:'design',families:[FONT,MONO]},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify(result));
