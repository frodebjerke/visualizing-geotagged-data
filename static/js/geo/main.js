/*global $, OpenLayers, TrackLayer, MapLayer, assert, assertNumber*/

"use strict";

var geographic = new OpenLayers.Projection("EPSG:4326"),
    spherical = new OpenLayers.Projection("EPSG:900913"),
    mapLayer = null,
    map = null,
    trackLayer = null,
    markerLayer = null,
    $loading,$map,$controls,$reset;


/**
 * @public
 * @description Fetches the graph for the selected mode
 */
function updateMap(){
   var mode = parseInt($controls.find("option:selected").val());
    mapLayer.update(mode);
}

/**
 * @public
 * @description Binds listener for loading overlay, mode selection, reset and the like
 */
function bindListener(){

    $loading.css({
	top : $map.position().top,
	left : $map.position().left
    });
    
    $("select[name=transportation]").change(function(){
	$reset.trigger("click");
	updateMap();
    });

    $map
	.bind("updateStart.geo",function(){
	    $controls.attr("disabled",true);
	    $loading.show();
	})
	.bind("updateStop.geo",function(){
	    $controls.attr("disabled",false);
	    $loading.hide();

	});

   // destroy the current trace
    $reset.click(function(){
	mapLayer.resetSelectedFeatures();
	trackLayer.destroy();
    });
}


$("body").bind("cLoad",function(){

    $loading = $(".map-loading");
    $map = $("#map");
    $controls = $("select,button");
    $reset = $("#reset");

    //binds listener for ui elements
    bindListener();

    //init map
    map = new OpenLayers.Map({
       div : "map",
       layers : [new OpenLayers.Layer.OSM()],
       controls : [new OpenLayers.Control.Navigation()],
       projection : "EPSG:4326"
    });

    trackLayer = new TrackLayer(map);
    mapLayer = new MapLayer(map,trackLayer);
    markerLayer = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markerLayer);
    updateMap();
});

function toPoint(jpoint){
    return new OpenLayers.Geometry.Point(
       parseFloat(jpoint.lon),
       parseFloat(jpoint.lat))
      .transform(geographic,spherical);
}

function toVector(geometry){
    return new OpenLayers.Feature.Vector(geometry);
}

function toVectors(pair){
   var source = pair[0],
       target = pair[1],
       sourcePoint = toPoint(source),
       targetPoint = toPoint(target);
    sourcePoint.geo_id = source.id;
    targetPoint.geo_id = target.id;
    return([
	    toVector(sourcePoint),
	    toVector(targetPoint),
	    toVector(new OpenLayers.Geometry.LineString([sourcePoint,targetPoint]))
    ]);
}


function pointToVector(jpoint){
    return new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(
	parseFloat(jpoint.lon),
	parseFloat(jpoint.lat))
	.transform(geographic,spherical));

}






