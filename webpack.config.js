const fs = require('fs');
const path = require('path');
const webcomponents = [
  '@spectrum-web-components/checkbox/sp-checkbox.js',
  '@polymer/paper-checkbox/paper-checkbox.js',
  '@polymer/iron-form/iron-form.js',
  '@polymer/paper-input/paper-input.js',
  '@polymer/paper-button/paper-button.js',
];

const files_to_copy = [
  ['node_modules/jquery/dist/jquery.min.js', 'app/static/dist/jquery.min.js'],
  ['node_modules/bootstrap/dist/css/bootstrap.min.css', 'app/static/dist/bootstrap.min.css'],
  ['node_modules/bootstrap/dist/css/bootstrap.min.css.map', 'app/static/dist/bootstrap.min.css.map'],
  ['node_modules/bootstrap/dist/js/bootstrap.min.js', 'app/static/dist/bootstrap.min.js'],
  ['node_modules/bootstrap/dist/js/bootstrap.min.js.map', 'app/static/dist/bootstrap.min.js.map'],
  ['app/scr/css/global.css', 'app/static/dist/global.css'],
];

for (const [src, dest] of files_to_copy) {
  fs.copyFile(path.resolve(__dirname, src), path.resolve(__dirname, dest), (err) => {
    if (err) throw err;
    console.log(`${dest.replace(__dirname, '')} was copied`);
  });
}

module.exports = {
  mode: 'production',
  entry: {
    'global.js': path.resolve(__dirname, 'app/scr/js/global.js'),
  },
  output: {
    publicPath: '',
    path: path.resolve(__dirname, 'app/static/dist'),
    filename: '[name]'
  },
}

for (const component of webcomponents) {
  module.exports.entry['webcomponents/'+component] = path.resolve(__dirname, 'node_modules', component);
}