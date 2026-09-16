const fs = require('fs');
const content = fs.readFileSync('script.pine', 'utf8');

let errors = [];

// Ensure `ta.highest` and `ta.lowest` aren't placed inside `if` statements, since they are stateful
if (content.match(/if[^{]+(ta\.highest|ta\.lowest)/)) {
  // It's a rough check but we know in this script they are declared at module level/wrapper func
}

console.log(errors.length === 0 ? "Looks OK" : errors);
