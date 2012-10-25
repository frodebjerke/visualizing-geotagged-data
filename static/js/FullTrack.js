MapLayer = function(map,onSelect){
    this.map = map;
    this.onSelect = onSelect;
}

MapLayer.prototype = {
    init : function(){
	if (this.layer){
	    this.map.removeLayer(this.layer);
	}

	this.layer = new OpenLayers.Layer.Vector("Full Track",  {

	    styleMap : new OpenLayers.StyleMap({
		"default" : defaultStyle,
		select : selectedStyle
	    }),
	    projection: geographic
	});

	this.initControls();
    },
    initControls : function(){

	if (this.select){
	    this.map.removeControl([
		this.select,
		this.pointSelect,
		this.panel]);
	}
	
	this.initSnap();

	this.initSelect();

	this.initPointSelect();



	this.initPanel();

    },
    initSnap : function(){
	this.snap = new OpenLayers.Control.Snapping({
	    layer :  this.layer,
	    tolerance : 100,
	    targets : [{
		layer: this.layer,
	    }],
	    edge : false,
	    eventListeners : {
		"snap" : function(event){
		    point = event.point
		    point = point.transform(spherical,geographic);

		},
	    }
	});
	this.map.addControl(this.snap);
	this.snap.activate();
    },
    initSelect : function(){
	this.select = new OpenLayers.Control.SelectFeature(this.layer,{
	    highlightOnly : true,
	    hover : true
	});
	this.map.addControl(this.select);
	this.select.activate();
    },
    initPointSelect : function(){
	//layers selected features array
	this.pointSelect = new OpenLayers.Control.SelectFeature(this.layer,{
	    hover : false,
	    multiple : true,
	    clickout : true,
	    toggle : true,
	    geometryTypes : ["OpenLayers.Geometry.Point"],	
	    onSelect : this.onSelect
	});
	this.map.addControl(this.pointSelect);
	this.pointSelect.activate();
    },
    initPanel : function(){
	this.panel = new OpenLayers.Control.Panel({
	    displayClass: "olControlEditingToolbar"
	});
	draw = new OpenLayers.Control.DrawFeature(
	    mapLayer, OpenLayers.Handler.Path,
	    {displayClass: "olControlDrawFeaturePath", title: "Draw Features"}
	);
	this.panel.addControls([
	    new OpenLayers.Control.Navigation({title: "Navigate"}),
	    draw,
	]);
	this.map.addControl(this.panel);
	
    },
    getSelectedFeatures : function(){
	return this.layer.selectedFeatures;
    },
    update : function(mode){
	this.init();
	var instance = this;
	$(".window").trigger("updateStart.geo");
	$.ajax({
	    url : "/track",
	    data : {
		"mode" : mode
	    },
	    dataType : "json",
	    success : function(pairs){
		pairs.forEach(function(pair){
		    vectors = toVectors(pair);
		    instance.layer.addFeatures(vectors);		
		});
		instance.map.addLayer(instance.layer);
		$(".window").trigger("updateStop.geo");
	    }
	});
    },
};



    

