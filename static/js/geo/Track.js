/*global $, toPoint, toVector, OpenLayers, assertNumber */

"use strict";

/**
 * @public 
 * @author Frederik Claus <f.v.claus@googlemail.com>
 * @description Models a trace from points, adding connections automatically.
 */
var Trace = function(){
   this.segments = [];
},
    Segment = null,
    TrackFeature = null,
    TrackPoint = null,
    TrackConnection = null;

Trace.prototype = {
   add : function(jpoint){
      var pointSrc = jpoint.src;
      if (this.src !== pointSrc){
	 this.tmpSegment = new Segment(pointSrc);
	 this.segments.push(this.tmpSegment);
	 this.src = pointSrc;

      }
      this.tmpSegment.add(jpoint);
   },
   toFeatures : function(){
      var features = [];
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
   setActive : function(src, id){
      var i = 0,
          segment = null;
      for (i = 0; i< this.segments.length; i++){
	 segment = this.segments[i];
	 if (segment.src === src){
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

      if (!this.segment || time === null){
	 console.log("need active segment and time to proceed. time : %d , active : %s",time,this.active);
	 return;
      }

      var instance = this,
          i = 0,
          segment,
          time = parseInt(time);
      
      this.active = this.segment.proceed(time);

      //either there is another segment with another video after the current one
      //or it is the last one 
      if (this.active === null && this.segmentIndex !== this.segments.length -1){
	 for (i = this.segmentIndex+1; i<this.segments.length; i++){
	    segment = this.segments[i];
	    if (segment.src !== null){
	       this.segment = segment;
	       this.segmentIndex = i;
	       this.active = this.segment.start();
	       break;
	    }
	 }
      }
      
      return this.active;
      
   },
   getNext  : function () {
      // try the next feature of the current segment
      var next = this.segment.getNext();

      if (next === null) {
         if (this.segmentIndex === this.segments.length - 1) {
            // last feature of last segment
            return null;
         } else {
            // return first feature of next segment
            return this.segments[this.segmentIndex + 1].getFeature(0);
         }
      } else {
         return next;
      }
   }
};

/**
 * @public 
 * @description Resembles a trackseg from gpx. Consists of points and connections with the same video url
 */
Segment = function(src){
   this.features = [];
   this.time = 0;
   this.timetoFeature = {};
   this.src = src;
};

Segment.prototype = {
   add : function(jpoint){
      var target = new TrackPoint(jpoint);

      if(this.source){
	 this.features.push(new TrackConnection(this.source,target));
      }
      this.features.push(target);
      this.source = target;
   },
   toFeatures : function(){
      var features = [];
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
      var i = 0,
          feature = null;
      for (i = 0; i< this.features.length; i++){
	 feature = this.features[i];
	 if (feature.getData("id") === id){
	    this.active = feature;
	    break;
	 }
      }
   },
   start : function(){
      var instance = this,
          i = 0,
          feature = null;
      for (i = 0; i<this.features.length; i++){
	 feature = this.features[i];
	 if (feature.getData("src") !== null){
	    this.active = feature;
	    break;
	 }
      }
      return this.active;
   },
   proceed : function(time){
      
      if (this.timetoFeature[time] !== undefined){
	 return this.timetoFeature[time];
      }


      // console.log("indexOld %d",indexOld);
          
      var features = this.features,
          feature = null,
          active = null,
          i = 0;

      //find the first feature where the current playback time fits
      for (i = 0; i < features.length; i++){
	 feature = features[i];
         // there will be a TrackPoint after this TrackConnection that we 'really' selected
         if (feature.getData("videotimeend") === time && feature instanceof TrackConnection) {
            continue;
         }
	 //search for the first segment that holds the time marker 
	 if (feature.getData("videotimestart") <= time && feature.getData("videotimeend") >= time && feature.getData("src") !== null){
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
	 if (feature === search){
	    position = index;
	 }
      });
      return position;
   },
   getFeature : function (index) {
      if (index >= this.features.length) {
         throw new Error(index + " is not a valid index");
      } else {
         return this.features[index];
      }
   },
   getNext : function () {
      var index = this.getIndex(this.active);
      assertNumber(index);

      if (index === this.features.length - 1) {
         return null;
      } else {
         return this.features[index+1];
      }
   }
};


/**
 * @public
 * @description Consists of data and a graphical representation
 */
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
   var data = null;
   //both on the same track add make the connection start when the source ends and end when the target starts
   if (source.getData("src") === target.getData("src")){
      data = $.extend({}, target.data);
      data.videotimestart = source.data.videotimeend;
      data.videotimeend = target.data.videotimestart;
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