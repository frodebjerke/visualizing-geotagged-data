Track = function(){
    this.source = null;
    this.features = [];
    this.active = 0;
};

Track.prototype = {
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
	return this.features[this.active];
    },
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
};

TrackPoint.protoype = new TrackFeature();

TrackPoint.prototype.getPoint = function(){
	return this.point;
};


TrackConnection = function(source,target){
    TrackFeature.call(this,source.data);
    this.vector = toVector(
	new OpenLayers.Geometry.LineString([
	    source.getPoint(),
	    target.getPoint()]));
	
};

TrackConnection.prototype = new TrackFeature();