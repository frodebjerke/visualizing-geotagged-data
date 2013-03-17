/*global trackLayer, toVector, toPoint, assertNumber */

"use strict";

var geo = {
   /**
    * @public
    * @returns {OpenLayers.Layer.Vector} Layer that is used to display the shortest trace. 
    * The layer will be removed, but not destroyed, upon reset. 
    */
   getTraceLayer : function () {
      return trackLayer.getVectorLayer();
   },
   /**
    * @public
    * @description Useful for building more complex geometries like LineStrings or Polygons
    * @returns OpenLayers.Geometry.Point
    * @param {String or Number} lat
    * @param {String or Number} lon
    */
   toPoint : function (lat, lon) {
      try {
         if (typeof lat === "string") {
            lat = parseFloat(lat);
         }
         if (typeof lon === "string") {
            lon = parseFloat(lon);
         }
      } catch (error) {
         throw new Error("Either lat or lon could not be parsed as a float.");
      }
      assertNumber(lat, "Lat must be a float.");
      assertNumber(lon, "Lon must be a float.");

      return toPoint({"lat" : lat, "lon" : lon});
   }
};