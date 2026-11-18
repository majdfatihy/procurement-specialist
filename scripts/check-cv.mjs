import fs from 'node:fs';
import assert from 'node:assert/strict';
const site=fs.readFileSync('index.html','utf8');
const ats=fs.readFileSync('cv-ats.html','utf8');
const has=(content,value,label)=>assert.ok(content.includes(value),label);
has(site,'<title>ماجد فتحي | أخصائي مشتريات','SEO page title');
has(site,'rel="canonical" href="https://dev.majdfatihy.com/procurement-specialist/"','canonical URL');
has(site,'id="main-title"','semantic main heading');
assert.equal((site.match(/<h1\b/g)||[]).length,1,'Exactly one visible H1');
has(site,'id="motionToggle"','motion accessibility toggle');
has(site,'href="./cv-ats.html"','ATS download link');
has(site,'id="education"','separate academic discipline');
has(site,'https://api.whatsapp.com/send?phone=201066732514','direct WhatsApp contact');
has(site,'https://t.me/majdfatihy','direct Telegram account');
has(site,'info@majdfatihy.com','professional email');
has(site,'id="print-cv"','print CV');
has(site,'#print-cv{display:block!important','A4 print mode');
has(ats,'rel="canonical" href="https://dev.majdfatihy.com/procurement-specialist/"','ATS canonical');
has(ats,'name="robots" content="noindex,follow"','avoid ATS SEO duplicate');
for(const bad of ['7,551,859','112,878','105,000','الايرادات','إيرادات الشركة']) {
  assert.ok(!site.includes(bad) && !ats.includes(bad),'Never publish confidential company data: '+bad);
}
const match=site.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
assert.ok(match,'Schema Person/ProfilePage is present');
const schema=JSON.parse(match[1]);
assert.ok(schema['@graph'].some(x=>x['@type']==='ProfilePage'),'ProfilePage schema');
assert.ok(schema['@graph'].some(x=>x['@type']==='Person'),'Person schema');
console.log('PASS: SEO, privacy, links, ATS, print structure and motion accessibility.');
