Trace = function(){
    this.segments = new Array();
};
//builds a trace from a bunch of points, adding connections and wrapping all elements
Trace.prototype = {
    add : function(jpoint){
	pointSrc = jpoint["src"]
	if (this.src != pointSrc){
	    this.tmpSegment = new Segment(pointSrc);
	    this.segments.push(this.tmpSegment);
	    this.src = pointSrc;

	}
	this.tmpSegment.add(jpoint);
    },
    toFeatures : function(){
	features = new Array();
	this.segments.forEach(function(segment){
	    features = features.concat(segment.toFeatures());
	});
	return features;
    },
    getActive : function(time){
	if(!this.segment){
	    return this.start();
	}
	return this.segment.getActive();
    },
    setActive : function(src,id){

	for (i = 0; i< this.segments.length; i++){
	    segment = this.segments[i];
	    if (segment.src == src){
		this.segment = segment;
		this.segmentIndex = i;
		break;
	    }
	}

	this.segment.setActive(id);
    },
    //pick the fist feature with a video of the first segment
    start : function(){
	this.segment = this.segments[0];
	this.segmentIndex = 0;
	this.active = this.segments[0].start();
	return this.active;
    },
    //proceed to a certain time marker
    proceed : function(time){

	if (!this.segment || time == null){
	    console.log("need active segment and time to proceed. time : %d , active : %s",time,this.active);
	    return;
	}

	var instance = this;

	time = parseInt(time);
	
	this.active = this.segment.proceed(time);

	//either there is another segment with another video after the current one
	//or it is the last one 
	if (this.active == null && this.segmentIndex != this.segments.length -1){
	    for (i = this.segmentIndex+1; i<this.segments.length; i++){
		segment = this.segments[i];
		if (segment.src != null){
		    this.segment = segment;
		    this.segmentIndex = i;
		    this.active = this.segment.start();
		    break;
		}
	    }
	}
	
	return this.active;
	    
    },

	
	    
};

Segment = function(src){
    this.features = new Array();
    this.time = 0;
    this.timetoFeature = {};
    this.src = src;
};

Segment.prototype = {
    add : function(jpoint){
	target = new TrackPoint(jpoint);

	if(this.source){
	    con = new TrackConnection(this.source,target);
	    this.features.push(con);
	}
	this.features.push(target);
	this.source = target;
    },
    toFeatures : function(){
	features = [];
	this.features.forEach(function(feature){
	    features.push(feature.getVector());
	});
	return features;
    },
    getActive : function(){
	if(!this.active){
	    this.active = this.start();
	}
	return this.active;
    },
    setActive : function(id){
	for (i = 0; i< this.features.length; i++){
	    feature = this.features[i];
	    if (feature.getData("id") == id){
		this.active = feature;
		break;
	    }
	}
    },
    start : function(){
	var instance = this;
	for (i = 0; i<this.features.length; i++){
	    feature = this.features[i];
	    if (feature.getData("src") != null){
		this.active = feature;
		break;
	    }
	}
	return this.active;
    },
    proceed : function(time){
	
	if (this.timetoFeature[time] != null){
	    return this.timetoFeature[time];
	}

	indexOld = this.getIndex(this.active);
	console.log("indexOld %d",indexOld);
	var srcOld = this.active.getData("src");
	// backward = (this.time > time)? true : false;
	// this.time = time;
	// console.log("backward",backward);
	//start looking in the features after the active one first

	// if (backward){
	//     features = this.features.splice(0,indexOld);
	//     features = features.filter(function(feature){
	// 	if (feature.getData("src") != srcOld){
	// 	    return false;
	// 	}
	// 	else{
	// 	    return true;
	// 	}
	//     });
	//     feature.reverse();
	// }
	// else{
	features = this.features;
	// }
	console.log(features);
	var active = null;
	//find the first feature where the current playback time fits
	for (i = 0; i < features.length; i++){
	    feature = features[i];
	    //search for the first segment that holds the time marker 
	    if (feature.getData("videotimestart") <= time && feature.getData("videotimeend") >= time && feature.getData("src") != null){
		active = feature;
		break;
	    }
	}

	this.active = active;
	this.timetoFeature[time] = active;

	return this.active;
    },
    getIndex : function(search){
	var position = null;
	this.features.forEach(function(feature,index){
	    if (feature == search){
		position = index;
	    }
	});
	return position;
    }

};



TrackFeature = function(data){this.data = data;};
TrackFeature.prototype = {
    getVector : function(){
	return this.vector;
    },
    getData : function(key){
	return this.data[key];
    }
};

TrackPoint = function(jpoint){
    TrackFeature.call(this,jpoint);
    this.point = toPoint(jpoint);
    this.vector = toVector(this.point);
    this.vector.geo_data = this.data;
};

TrackPoint.prototype = new TrackFeature();

TrackPoint.prototype.getPoint = function(){
	return this.point;
};


TrackConnection = function(source,target){
    //both on the same track add make the connection start when the source ends and end when the target starts
    if (source.getData("src") == target.getData("src")){
	data = $.extend({}, target.data);
	data["videotimestart"] = source.data["videotimeend"];
	data["videotimeend"] = target.data["videotimestart"];
    }
    //both on a different track only use the data from the target
    else if (target.getData("src")){
	data = $.extend({},target.data);
    }
    //both on no track use nothing
    else{
	data = {};
    }
    TrackFeature.call(this,data);
    this.vector = toVector(
	new OpenLayers.Geometry.LineString([
	    source.getPoint(),
	    target.getPoint()]));
    this.vector.geo_data = this.data;
	
};

TrackConnection.prototype = new TrackFeature();