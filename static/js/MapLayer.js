MapLayer = function(map,track){
    this.map = map;
    this.mode = null;
    this.track = track;
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
	//init function remove control first and then add it again
	this.initSnap();
	this.initSelect();
	this.initPointSelect();
	this.initPanel();

    },
    initSnap : function(){
	if (this.snap){
	    this.map.removeControl(this.snap);
	}
	this.snap = new OpenLayers.Control.Snapping({
	    layer :  this.layer,
	    tolerance : 100,
	    targets : [{
		layer: this.layer,
	    }],
	    edge : false,
	    eventListeners : {
		"snap" : function(event){
		    alert("snap");
		    point = event.point
		    point = point.transform(spherical,geographic);

		},
	    }
	});
	this.map.addControl(this.snap);
	this.snap.activate();
    },
    //highlight only select
    initSelect : function(){
	if (this.select){
	    this.map.removeControl(this.select);
	}
	this.select = new OpenLayers.Control.SelectFeature(this.layer,{
	    highlightOnly : true,
	    hover : true
	});
	this.map.addControl(this.select);
	this.select.activate();
    },
    //tracklayer point selection
    initPointSelect : function(){
	if (this.pointSelect){
	    this.map.removeControl(this.pointSelect);
	}
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
	if (this.panel){
	    this.map.removeControl(this.panel);
	}
	this.panel = new OpenLayers.Control.Panel({
	    displayClass: "olControlEditingToolbar"
	});
	draw = new OpenLayers.Control.DrawFeature(
	    this.map, OpenLayers.Handler.Path,
	    {displayClass: "olControlDrawFeaturePath", title: "Draw Features"}
	);
	this.panel.addControls([
	    new OpenLayers.Control.Navigation({title: "Navigate"}),
	    draw,
	]);
	this.map.addControl(this.panel);
	
    },
    disableControls : function(){
	this.panel.deactivate();
	this.pointSelect.deactivate();
	this.select.deactivate();
    },
    enableControls : function(){
	this.panel.activate();
	this.pointSelect.activate();
	this.select.activate();

    },

    //gets graph of a certain mode displays it and centers the map
    update : function(mode){
	this.init();
	var instance = this;
	
	$map.trigger("updateStart.geo");
	this.mode = mode;
	$.ajax({
	    url : "/track/",
	    data : {
		"mode" : this.mode
	    },
	    dataType : "json",
	    success : function(pairs){
		pairs.forEach(function(pair){
		    vectors = toVectors(pair);
		    instance.layer.addFeatures(vectors);		
		});
		instance.map.addLayer(instance.layer);
		center = instance.getCenter();

		instance.map.setCenter(center, // Center of the map
    			      15 // Zoom level
    			     );

		$map.trigger("updateStop.geo");
	    }
	});
    },
    getMode : function(){
	return this.mode;
    },
    getCenter : function(){
	//gets the center from the bounding box that holds all layer features
	extent = this.layer.getDataExtent();
	if (extent){
	    return extent.getCenterLonLat();
	}
	return null;
    },
    resetSelectedFeatures : function(){
	this.select.unselectAll();
    },
    //select listener for point select
    onSelect : function(){

	var instance = mapLayer;
	var selectedFeatures = this.layer.selectedFeatures;
	length = selectedFeatures.length;
	
	if (length > 2){
	    alert("Select only two points.");
	}

	if (length > 1){
	    source = selectedFeatures[length -2].geometry.geo_id;
	    target = selectedFeatures[length -1].geometry.geo_id;

	    if (!source || !target){
		alert("Could not retrieve source or target id");
		return;
	    }
	    
	    //trigger updatestart to display loading and disable ui
	    $map.trigger("updateStart");
	    $.ajax({
		url : "/track/",
		data : {
		    "mode" : instance.mode,
		    "source" : source,
		    "target" : target
		},
		dataType : "json",
		success : function(points){
		    if (points.length == 0){
			alert("No connection beetween the two points");
		    }
		    else{
			instance.track.update(points);
			instance.resetSelectedFeatures();
		    }
		    $map.trigger("updateStop");	
		},
		error : function(jqXHR){
		    alert("The server seems to have trouble responding at the moment.");
		    instance.resetSelectedFeatures();
		    $map.trigger("updateStop");	
		}

	    });
	    
	}
    }
    
};



    

