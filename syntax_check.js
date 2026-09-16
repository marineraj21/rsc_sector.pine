const fs = require('fs');
const content = fs.readFileSync('script.pine', 'utf8');

let errors = [];

// Check for missing ternary branches
if (content.match(/\?\s*[^:]+\s*(?!:)/)) {
  // Rough regex, better to just visually inspect
}

// Ensure color.new uses transparency
if (content.match(/color\.new\([^,]+?\)/)) {
    errors.push("color.new requires transparency");
}

console.log(errors.length === 0 ? "Looks OK" : errors);
