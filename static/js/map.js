var geographic = new OpenLayers.Projection("EPSG:4326");
var spherical = new OpenLayers.Projection("EPSG:900913");
var mapLayer,map,trackLayer;

var defaultStyle = {
    strokeWidth : 3,
    strokeOpacity : 0.4,
    strokeColor : "red",
    pointRadius : 3,
    pointColor : "red",
    pointOpacity : 0.6,
    fillColor : "red",

};

var selectedStyle = {
    strokeOpacity : 0.8,
    pointColor : "green",
    strokeColor : "green",
    pointOpacity : 1,
    fillColor : "green"
};

var trackStyle = {
    pointColor : selectedStyle.pointColor,
    strokeColor : selectedStyle.strokeColor,
    fillColor : selectedStyle.fillColor,
    strokeWidth : defaultStyle.strokeWidth * 1.5,
    pointRadius : defaultStyle.pointRadius * 1.5
};

var activeStyle = {
    pointColor : "blue",
    strokeColor : "blue",
    fillColor : "blue",
    strokeWidth : trackStyle.strokeWidth,
    pointRadius : trackStyle.pointRadius
};

var $loading,$map,$controls,$reset;

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
    	controls : [new OpenLayers.Control.Navigation(),
    		    new OpenLayers.Control.LayerSwitcher(),
    		    new OpenLayers.Control.Attribution()],
    });

    trackLayer = new TrackLayer(map);
    

    mapLayer = new MapLayer(map,trackLayer);
    updateMap();



});

function updateMap(){
    mode = parseInt($controls.find("option:selected").val());
    mapLayer.update(mode);
}


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

    $reset.click(function(){
	mapLayer.resetSelectedFeatures();
	trackLayer.destroy();
    });
}



function toVectors(pair){
    source = pair[0];
    target = pair[1];
    sourcePoint = toPoint(source);
    targetPoint = toPoint(target);
    sourcePoint.geo_id = source.id;
    targetPoint.geo_id = target.id;
    return([
	    toVector(sourcePoint),
	    toVector(targetPoint),
	    toVector(new OpenLayers.Geometry.LineString([sourcePoint,targetPoint]))
    ]);
}

function toPoint(jpoint){
    return new OpenLayers.Geometry.Point(
	parseFloat(jpoint.lon),
	parseFloat(jpoint.lat))
	.transform(geographic,spherical)
}

function toVector(geometry){
    return new OpenLayers.Feature.Vector(geometry);
}

function pointToVector(jpoint){
    return new OpenLayers.Feature.Vector(new OpenLayers.Geometry.Point(
	parseFloat(jpoint.lon),
	parseFloat(jpoint.lat))
	.transform(geographic,spherical));

}






