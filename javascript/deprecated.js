"use strict";

var deprecationText = `
---
warning: type \`{}\` is deprecated. use \`struct\` instead.

See https://github.com/jfjlaros/bin-parser#basic-types for more information.
---
`;

function deprecationWarning(message) {
  if (this.showDepricationWarning === undefined) {
    console.log(deprecationText.replace("{}", message));
    this.showDepricationWarning = false;
  }
}

module.exports = {
  "deprecationWarning": deprecationWarning
};
