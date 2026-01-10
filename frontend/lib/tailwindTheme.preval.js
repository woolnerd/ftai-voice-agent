const preval = require("next-plugin-preval/macro");
const colors = require("tailwindcss/colors");

const customColors = {
  cyan: colors.cyan,
  green: colors.green,
  amber: colors.amber,
  violet: colors.violet,
  blue: colors.blue,
  rose: colors.rose,
  pink: colors.pink,
  teal: colors.teal,
  red: colors.red,
};

const theme = {
  colors: {
    transparent: "transparent",
    current: "currentColor",
    black: colors.black,
    white: colors.white,
    gray: colors.neutral,
    ...customColors,
  },
};

module.exports = preval(theme);
