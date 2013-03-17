/*global $*/

"use strict";

var styles = {
   "default" : {
      strokeWidth : 3,
      strokeOpacity : 0.4,
      strokeColor : "red",
      pointRadius : 3,
      pointColor : "red",
      pointOpacity : 0.6,
      fillColor : "red",

   },

   "selected" : {
       strokeOpacity : 0.8,
       pointColor : "green",
       strokeColor : "green",
       pointOpacity : 1,
       fillColor : "green"
    }
};

styles.track = {
       pointColor : styles.selected.pointColor,
       strokeColor : styles.selected.strokeColor,
       fillColor : styles.selected.fillColor,
       strokeWidth : styles.default.strokeWidth * 1.5,
       pointRadius : styles.default.pointRadius * 1.5
};

styles.active = {
       pointColor : "blue",
       strokeColor : "blue",
       fillColor : "blue",
       strokeWidth : styles.track.strokeWidth,
       pointRadius : styles.track.pointRadius
};

styles.boundingBox = {
   pointColor : "orange",
   pointRadius : styles.track.pointRadius,

   strokeColor : "orange",
   strokeWidth : styles.track.strokeWidth,
   strokeOpacity : 0.3,
   
   fillColor : "orange",
   fillOpacity : 0.3,

   // graphicZIndex : -10
};





