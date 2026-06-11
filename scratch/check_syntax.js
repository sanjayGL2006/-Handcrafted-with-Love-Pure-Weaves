const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('index.html', 'utf8');
const lines = html.split('\n');
// Extract script contents between line 2325 and 3424 (0-indexed line 2325 is index 2325 in 0-indexed split)
// Line 2325 is <script> and 3424 is </script>
const scriptLines = lines.slice(2325, 3423); 
const code = scriptLines.join('\n');

try {
  new vm.Script(code);
  console.log("Syntax OK!");
} catch (e) {
  console.error("Syntax Error at:", e.stack);
}
