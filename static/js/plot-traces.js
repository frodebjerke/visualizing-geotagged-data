/*global document, OpenLayers, $, geographic, spherical */
"use strict";


var lat=49.487689,
    lon=8.466232,
    zoom=16;

function createGPXLayer(name, color) {
   return new OpenLayers.Layer.Vector(name, {
      strategies: [new OpenLayers.Strategy.Fixed()],
      protocol: new OpenLayers.Protocol.HTTP({
         url: "/static/traces/" + name + ".gpx",
         format: new OpenLayers.Format.GPX()
      }),
      style: {strokeColor: color, strokeWidth: 5, strokeOpacity: 0.8},
      projection: geographic
   });
}
      

function createGPXLayers () {
   var TRACES_FORTH = ["Track201210311143", // 1
                       "Track201210311152", // 2
                       "Track201210311207", // 3
                       "Track201210311340"], // 7
   TRACES_BACK = ["Track201210311435", // 1
                  "Track201210311219", // 2
                  "Track201210311214", // 3
                  "Track201210311312", // 5
                  "Track201210311343", // 7
                  "Track201210311425"], // 9
       traces = [];

   TRACES_FORTH.forEach(function (trace) {
      traces.push(createGPXLayer(trace, "green"));
   });
   TRACES_BACK.forEach(function (trace) {
      traces.push(createGPXLayer(trace, "blue"));
   });
   return traces;
}

$(document).ready(function () {
   // $("a[href='#map-original-tab']").click(function () {
   var map = new OpenLayers.Map ({
      div: "map-original",
      controls:[
         new OpenLayers.Control.Navigation(),
         // new OpenLayers.Control.PanZoomBar(),
         // new OpenLayers.Control.LayerSwitcher(),
         // new OpenLayers.Control.Attribution()
      ],
      // maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
      // maxResolution: 156543.0399,
      // numZoomLevels: 19,
      // units: 'm',
      // projection: new OpenLayers.Projection("EPSG:900913"),
      // displayProjection: new OpenLayers.Projection("EPSG:4326")
   }),
       layerMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik"),
       layerCycleMap = new OpenLayers.Layer.OSM.CycleMap("CycleMap"),      
       layerMarkers = new OpenLayers.Layer.Markers("Markers"),
       lonLat = new OpenLayers.LonLat(lon, lat)
          .transform(geographic, spherical),
       traceLayers = createGPXLayers();

   map.addLayer(layerMapnik);
   // map.addLayer(layerCycleMap);
   // map.addLayer(layerMarkers);
   traceLayers.forEach(function (layer) {
      map.addLayer(layer);
   });
   map.setCenter(lonLat, zoom);
   
   // var size = new OpenLayers.Size(21, 25);
   // var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
   // var icon = new OpenLayers.Icon('http://www.openstreetmap.org/openlayers/img/marker.png',size,offset);
   // layerMarkers.addMarker(new OpenLayers.Marker(lonLat,icon));
   // });
});


   

   


