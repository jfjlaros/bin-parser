'use strict';

var deprication_text = `
---
warning: type \`{}\` is depricated. use \`struct\` instead.

See https://github.com/jfjlaros/bin-parser/blob/master/README.md#basic_types
for more information.
---
`;

function deprication_warning(message) {
  if (this.show_deprication_warning === undefined) {
    console.log(deprication_text.replace('{}', message));
    this.show_deprication_warning = false;
  }
}

module.exports = {
  'deprication_warning': deprication_warning
};
