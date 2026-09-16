const fs = require('fs');
let content = fs.readFileSync('script.pine', 'utf8');

const replacement = `update_zones(array<Zone> arr) =>
    if array.size(arr) > 0
        for i = 0 to array.size(arr) - 1
            Zone z = array.get(arr, i)
            box.set_right(z.b, bar_index)
            if show_labels
                label.set_x(z.l, bar_index + 2)`;

content = content.replace(/update_zones\(array<Zone> arr\) =>[\s\S]+?(?=\/\/ Execute Drawing TF1)/, replacement + '\n\n');
fs.writeFileSync('script.pine', content);
console.log('Fixed script.pine');
