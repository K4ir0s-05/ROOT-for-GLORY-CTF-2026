// baby rev 2 solver - GCDxGLORY CTF (author: K4ir0s)
// Usage: node solve.js [../files/obfuscJStor.js]
const fs = require('fs');
const vm = require('vm');
const file = process.argv[2] || __dirname + '/../files/obfuscJStor.js';
const src = fs.readFileSync(file, 'utf8');

// Method 1: make the domain check pass (fake `document.domain`)
const logs = [];
vm.runInNewContext(src, {
  document: { domain: 'obfuscator.io' },
  console: { log: (...a) => logs.push(a.join(' ')) },
});
console.log('[1] fake document.domain ->', logs.join(' | '));

// Method 2: read the string array, without running hi()
const ctx = vm.createContext({ document: { domain: '' }, console: { log() {} } });
vm.runInContext(src.replace(/hi\(\);\s*$/, ''), ctx);   // defines _0xarr / _0xd, does not call hi()
const arr = vm.runInContext('_0xarr()', ctx);            // already rotated 37 times
const OFFSET = 0x1ee;                                    // _0xd(i) returns arr[i - 0x1ee]
// the flag is the argument of the console.log that sits behind the domain check
const call = src.match(/&&console\[_0xd\(0x[0-9a-f]+\)\]\(((?:_0xd\(0x[0-9a-f]+\)\+?)+)\)/)[1];
const idx = [...call.matchAll(/_0xd\((0x[0-9a-f]+)\)/g)].map(m => parseInt(m[1], 16));
console.log('[2] indexes', idx.map(i => '0x' + i.toString(16)).join(' '), '->', idx.map(i => arr[i - OFFSET]).join(''));
