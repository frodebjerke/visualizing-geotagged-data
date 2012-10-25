ShortestTrack = function(){
    this.source = null;
    this.features = [];
    this.active = 0;
};

ShortestTrack.prototype = {
    add : function(jpoint){

	target = new ShortestTrackPoint(jpoint);

	if(this.source){
	    con = new ShortestTrackConnection(source,target);
	    this.features.push(con);
	}
	this.features.push(target);
	this.source = target;

    },
    toFeatures : {
	features = [];
	this.features.forEach(function(feature){
	    features.push(feature.getVector());
	});
	return features;
    },
    getActive : {
	return this.features[this.active];
    },
};


ShortestTrackFeature = function(data){this.data = data;};
ShortestTrackFeature.prototype = {
    getVector : function(){
	return this.vector;
    },
    getData : function(key){
	return this.data[key];
    }
};

ShortestTrackPoint = function(jpoint){
    ShortestTrackFeature.call(this,jpoint);
    this.point = toPoint(jpoint);
    this.vector = toVector(this.point);
};

ShortestTrackPoint.prototype = {
    this.getPoint : function(){
	return this.point;
    }
};

ShortestTrackConnection = function(source,target){
    ShortestTrackFeature.call(this,source.data);
    this.vector = toVector(
	new OpenLayers.Geometry.LineString([
	    source.getPoint(),
	    target.getPoint()]));
	
};

ShortestTrackConnection.prototype = {
};