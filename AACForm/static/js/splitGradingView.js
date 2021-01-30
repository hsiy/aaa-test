/**
   * Handles the adjustment of the width of the columns, uses Split.js library
   * @class grading_section
   */
  var splitobj = Split(["#one","#two"], {
    elementStyle: function (dimension, size, gutterSize) { 
        return {'flex-basis': 'calc(' + size + '% - ' + gutterSize + 'px)'}
    },
    gutterStyle: function (dimension, gutterSize) { return {'flex-basis':  gutterSize + 'px'} },
    sizes: [65,35],
    snapOffset: 0,
    gutterSize: 6,
    cursor: 'col-resize'
});