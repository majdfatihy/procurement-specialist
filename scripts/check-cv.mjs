import fs from 'node:fs';
import assert from 'node:assert/strict';
const site=fs.readFileSync('index.html','utf8');
const ats=fs.readFileSync('cv-ats.html','utf8');
const has=(content,value,label)=>assert.ok(content.includes(value),label);
has(site,'<title>ماجد فتحي | أخصائي مشتريات','SEO page title');
has(site,'rel="canonical" href="https://dev.majdfatihy.com/procurement-specialist/"','canonical URL');
has(site,'id="main-title"','semantic main heading');
assert.equal((site.match(/<h1\b/g)||[]).length,1,'Exactly one visible H1');
assert.ok(!site.includes('id="motionToggle"'),'Removed motion control must not return');
assert.ok(site.includes("var paused=reduced;"),'Respect reduced-motion preference without toggle');
has(site,'z-index:50;isolation:isolate;overflow:visible','Header above page content');
has(site,'z-index:100;top:calc(100% + 10px)','Dropdown above page content');
has(site,'<details class="mobile-menu">','Mobile section menu');
has(site,'#experience .timeline::after','Experience marker alignment');
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
const en=fs.readFileSync('en/index.html','utf8');
const build=fs.readFileSync('scripts/build-site.sh','utf8');
has(site,'hreflang="en" href="https://dev.majdfatihy.com/procurement-specialist/en/"','Arabic English alternate');
has(en,'rel="canonical" href="https://dev.majdfatihy.com/procurement-specialist/en/"','English canonical');
has(en,'hreflang="ar-EG" href="https://dev.majdfatihy.com/procurement-specialist/"','Reciprocal hreflang');
has(en,'<html lang="en" dir="ltr">','English language declaration');
assert.equal((en.match(/<h1\b/g)||[]).length,1,'English page has one heading');
for(const href of ['./majd-fatihy-cv-ar.pdf','./majd-fatihy-cv-ats.pdf','./en/']) {
  has(site,href,'Arabic action link '+href);
}
for(const href of ['../majd-fatihy-cv-en.pdf','../majd-fatihy-cv-ats.pdf']) {
  has(en,href,'English direct PDF link '+href);
}
for(const url of [
 'https://github.com/majdfatihy/image-compressor',
 'https://github.com/majdfatihy/facebook-contacts-converter',
 'https://github.com/majdfatihy/online-earning-directory'
]) {
  has(site,url,'Verified project link on Arabic CV');
  has(en,url,'Verified project link on English CV');
}
has(site,'id="practice"','Arabic procurement scenarios');
has(site,'id="projects"','Arabic independent projects');
has(en,'id="practice"','English procurement scenarios');
has(en,'id="projects"','English independent projects');
has(site,'class="mobile-quick-actions"','Arabic mobile contact and download');
has(en,'class="mobile-bar"','English mobile contact and download');
for(const file of ['majd-fatihy-cv-ar.pdf','majd-fatihy-cv-ats.pdf','majd-fatihy-cv-en.pdf']) {
  has(build,file,'PDF generated during the deployment: '+file);
}
for(const val of ['7,551,859','112,878','105,000','436','7,000 جنيه']) {
  assert.ok(!site.includes(val) && !en.includes(val), 'No confidential figures in public CV: '+val);
}
const schemaEn=JSON.parse(en.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1]||'{}');
assert.ok(schemaEn['@graph']?.some(x=>x['@type']==='ProfilePage'),'English ProfilePage structured data');
assert.equal((site.match(/GTM-KTQKNNC8/g)||[]).length,1,'Do not duplicate GTM on Arabic');
assert.equal((en.match(/GTM-KTQKNNC8/g)||[]).length,1,'Do not duplicate GTM on English');

const routing=fs.readFileSync('assets/js/cv-language.js','utf8');
const favicon='https://dev.majdfatihy.com/assets/img/procurement-specialist-majd-fatihy-favicon.jpg';
has(site,'rel="icon" type="image/jpeg" href="'+favicon+'"','Arabic page-specific favicon');
has(en,'rel="icon" type="image/jpeg" href="'+favicon+'"','English page-specific favicon');
has(site,'src="./assets/js/cv-language.js"','Arabic language script');
has(en,'src="../assets/js/cv-language.js"','English language script');
has(site,'href="./en/?lang=en"','Manual English language preference');
has(en,'href="../?lang=ar"','Manual Arabic language preference');
assert.ok(!en.includes('<p class="title-ar"'), 'English page must not show Arabic duplicate name');
has(routing,"localStorage.setItem(key, requested)",'Language choice saved');
has(routing,"navigator.languages",'Browser-language detection');
has(routing,"googlebot|bingbot",'Googlebot-safe access to both pages');
for(const name of ['cv-i-target','cv-i-sparkles','cv-i-briefcase','cv-i-package','cv-i-clipboard','cv-i-tool','cv-i-book','cv-i-code','cv-i-help','cv-i-mail','cv-i-users']) {
 has(site,'id="'+name+'"','Professional Arabic SVG icon '+name);
 has(en,'id="'+name+'"','Professional English SVG icon '+name);
}
has(site,'id="roles"','Arabic SEO job title section');
has(en,'id="roles"','English SEO job title section');
for(const phrase of ['أخصائي مشتريات','مسؤول مشتريات','منسق مشتريات','مشتريات صناعية','مشتريات مستلزمات معامل']) {
 has(site,phrase,'Arabic related purchasing specialization '+phrase);
}
for(const phrase of ['Procurement Specialist','Purchasing Specialist','Procurement Officer','Purchasing Officer','Technical Buyer','Packaging Procurement']) {
 has(en,phrase,'English related purchasing specialization '+phrase);
}

console.log('PASS: bilingual SEO, browser language, page-only favicon, icons, privacy and PDF downloads.');
