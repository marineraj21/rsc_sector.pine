const fs = require('fs');
const content = fs.readFileSync('script.pine', 'utf8');
if (content.includes('//@version=6')) {
  console.log('Version 6 present');
} else {
  console.log('Version 6 missing');
}
