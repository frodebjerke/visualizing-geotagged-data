TrackLayer = function(map){
    this.map  = map;
    var instance = this;

    $video = $("#video");
    width = $video.width();
    height = $video.height();
    
    this.player =  _V_("video");
    //mute player
    this.player.volume(0);
    this.player.size(width,height);


    this.player.addEvent("loadeddata",function(){
	//this is the video object
	this.addEvent("timeupdate",trackLayer.highlightUpdate);
	this.play();
	this.currentTime(instance.track.getActive().getData("videotimestart"));
    });

};

TrackLayer.prototype = {
    init : function(){
	// if (this.trackLayer){
	//     this.map.removeLayer(this.trackLayer);
	// }
	



	this.trackLayer  = new OpenLayers.Layer.Vector("TrackLayer",{
	    styleMap : new OpenLayers.StyleMap({
		"default" : trackStyle,
		"select" : activeStyle
	    }),
	    projection  : geographic
	});

	
	this.initControls();

    },
    destroy : function(){
	// if (this.select){
	//     this.select.deactivate();
	// }
	this.stopHighlight();
	// this.map.removeControl(this.select);
	if (this.trackLayer){
	    this.map.removeLayer(this.trackLayer);
	    this.trackLayer = null;
	}
	if (this.activeLayer){
	    this.map.removeLayer(this.activeLayer);
	    this.activeLayer = null;
	}
	mapLayer.enableControls();
    },
	
    initControls : function(){
	if (this.select){
	    this.map.removeControl(this.select);
	}
	this.select = new OpenLayers.Control.SelectFeature(this.trackLayer,{
	    multiple : false,
	    clickout : false,
	    toggle : false,
	    highlightOnly : true,
	    onSelect : function(feature){
		console.log(feature);
		alert ("select tracklayer");
	    },
	});

	if (this.highlight){
	    this.map.removeControl(this.highlight);
	}
	this.highlight = new OpenLayers.Control.SelectFeature(this.trackLayer,{
	    multiple : false,
	    clickout : false,
	    toggle : false,
	    highlightOnly : true,
	    onSelect : function(feature){
		var instance = trackLayer;
		//triggered by user
		if (!instance.ignoreSelect){
	    	    console.log("skipping...");

		    srcOld = instance.track.getActive().getData("src");
		    src = feature.geo_data.src;
		    videotimestart = feature.geo_data.videotimestart;

		    //hit a mapconnection do nothing
		    if (!videotimestart){
			alert("There is no video to show here.");
			return;
		    }
		    //hit another video. set active and load video
		    else if (srcOld != src){
			instance.stopHighlight();
			instance.track.setActive(src,feature.geo_data.id);
			instance.startVideo();
			return;
		    }
		    //still the same video. proceed to the current time marker
		    else{
			instance.player.currentTime(videotimestart);
			return;
		    }
		}			
	    }
	});

	
	this.map.addControl(this.select);
	this.map.addControl(this.highlight);
	this.select.activate();
	this.highlight.activate();
    },

    highlightFeature : function(){
	this.removeHighlight();
	this.ignoreSelect = true;
	this.highlight.select(this.track.getActive().getVector());
	this.ignoreSelect = false;
	this.isEnded = false;
    },
    removeHighlight : function(){
	this.highlight.unselectAll();
	this.isEnded = true;
    },
    //update reinitialises the layer and draws the points
    update : function(points){
	this.init();
	
	var source = null;
	var track = new Trace();
	var features = [];
	points.forEach(function(point){
	    track.add(point);
	});

	this.trackLayer.addFeatures(track.toFeatures());
	this.track = track;
	this.map.addLayer(this.trackLayer);
	this.map.setLayerIndex(this.trackLayer,999);

	this.startVideo();
    },
    startVideo : function(){
	var start = this.track.getActive();

	this.player.src({type:"video/ogg",src:start.getData("src")});
	console.log("start at %d with %s",start.getData("videotimestart"),start);
	// this.player.currentTime(start.getData("videotimestart"));

    },
    stopHighlight : function(){
	this.player.removeEvent("timeupdate",this.highlightUpdate);
    },
    highlightUpdate : function(){
	var instance = trackLayer;

	oldFeature = instance.track.getActive();
	//will return the next active feature of the track
	//this might be a track belonging to a different source
	console.log("proceed to ",this.currentTime());
	newFeature  = instance.track.proceed(this.currentTime());
	console.log("newFeature",newFeature);
	//end of video
	//dont remove listener yet -- this will be done in the layer destroy
	if (newFeature == null){
	    if (!instance.isEnded){
		instance.removeHighlight();
	    }
	    console.log("video ended");
	    // alert ("end");
	    // this.pause();
	    return;
	}
	//change of videos
	else if (oldFeature.getData("src") != newFeature.getData("src")){
	    console.log("video switched");
	    // alert("switch");
	    this.pause();
	    instance.stopHighlight();
	    //restart video
	    instance.startVideo();
	    return;
	}
	//video proceeds, hightlight currently playing segment
	if (oldFeature != newFeature){
	    console.log("video proceed");
	    instance.highlightFeature();
	}
    },
	
    // getTimeBuffered : function(){
    // 	timeRange = this.player.buffered();
    // 	buffered = timeRange.end(0) - timeRange.start(0);
    // 	return buffered;
    // }


};
    