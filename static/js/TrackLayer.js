/*global $, _V_, OpenLayers, MapLayer, styles, assert, assertTrue, geographic, onVideoProgress, Trace */

"use strict";

/**
 * @public
 * @author Frederik Claus <f.v.claus@googlemail.com>
 * @description Displays a trace between two points on the graph and hightlights the progress
 * @param {OpenLayers.Map} map
 */
var TrackLayer = function(map){
   assert(map.CLASS_NAME, "OpenLayers.Map");

   var instance = this,
       $video = $("#video"),
       width = $video.width(),
       height = $video.height();

   this.map  = map;
   this.player =  _V_("video");
   //mute player
   this.player.volume(0);
   this.player.size(width,height);

   // start playing as soon as the video metadata is fully loaded
   // update the current position of the trace
   this.player.addEvent("loadeddata",function(){
      //this is the video object
      this.addEvent("timeupdate", function () {
         instance._highlightUpdate.apply(instance);
      });
      this.play();
      this.currentTime(instance.track.getActive().getData("videotimestart"));
   });

   this.oldFeature = undefined;
   this.newFeature = undefined;

};

TrackLayer.prototype = {
   init : function(){
      assertTrue(typeof styles.track === "object");
      assertTrue(typeof styles.active === "object");

      this.trackLayer  = new OpenLayers.Layer.Vector("TrackLayer",{
	 styleMap : new OpenLayers.StyleMap({
	    "default" : styles.track,
	    "select" : styles.active
	 }),
	 projection  : geographic
      });

      
      this._initControls();

   },
   /**
    * @public
    * @description Removes the trace layer from the graph layer
    */
   destroy : function(){

      this._stopHighlight();

      if (this.trackLayer){
	 this.map.removeLayer(this.trackLayer);
	 this.trackLayer = null;
      }
      if (this.activeLayer){
	 this.map.removeLayer(this.activeLayer);
	 this.activeLayer = null;
      }
   },

   /**
    * @public
    * @description Reinitialises the layer and draws the points
    */
   update : function(points){
      assertTrue(points instanceof Array);
      assertTrue(points.length > 0);
      
      this.init();
      
      var source = null,
          track = new Trace(),
          features = [];
     
      // build the new trace
      points.forEach(function(point){
	 track.add(point);
      });
      
      // draw the trace on the layer
      this.trackLayer.addFeatures(track.toFeatures());
      // add the trace-layer to the map
      this.track = track;
      this.map.addLayer(this.trackLayer);
      this.map.setLayerIndex(this.trackLayer,999);

      this._startVideo();
   },
   /** 
    * @private
    * @description Starts the video belonging to the current active segment
    */
   _startVideo : function(){
      var start = this.track.getActive();

      this.player.src({type:"video/ogg",src:start.getData("src")});
      console.log("start at %d with %s",start.getData("videotimestart"),start);
   },
   /** 
    * @private
    * @description Removes the highlight listener from the video
    */
   _stopHighlight : function(){
      this.player.removeEvent("timeupdate",this._highlightUpdate);
   },
   /** 
    * @private
    * @description Highlight the current segment of the trace-layer
    */
   _highlightUpdate : function(){
      assertTrue(this instanceof TrackLayer);


      var oldFeature = this.track.getActive(),
          // will return the next active feature of the track
          // this might be a track belonging to a different source
          newFeature  = this.track.proceed(this.player.currentTime());


      // console.log("newFeature",newFeature);
      // inform others update the progress
      if (oldFeature !== newFeature) {
         onVideoProgress(newFeature, this.track.getNext());
      }
      // end of video
      // don't remove listener yet -- this will be done in the layer destroy
      if (newFeature === null){
	 if (!this.isEnded){
	    this._removeHighlight();
	 }
	 console.log("video ended");
	 return;
      } else if (oldFeature.getData("src") !== newFeature.getData("src")) { //change of videos
	 console.log("video switched");
	 // alert("switch");
	 this.player.pause();
	 this._stopHighlight();
	 // restart video
	 this._startVideo();
	 return;
      }
      // video proceeds, highlight currently playing segment
      if (oldFeature !== newFeature){
	 console.log("video proceed");
	 this._highlightFeature();
      }
   },
   /**
    * @private
    * @description Highlights the current visited segment (Point or Connection) of the trace
    */
   _highlightFeature : function(){
      this._removeHighlight();
      this.ignoreSelect = true;
      this.highlight.select(this.track.getActive().getVector());
      this.ignoreSelect = false;
      this.isEnded = false;
   },
   /**
    * @private
    * @description Remove the highlight from the layer.
    */
   _removeHighlight : function(){
      this.highlight.unselectAll();
      this.isEnded = true;
   },
   /**
    * @private
    */
   _initControls : function(){
      assert(this.trackLayer.CLASS_NAME, "OpenLayers.Layer.Vector");

      if (this.highlight){
	 this.map.removeControl(this.highlight);
      }

      // this will only hightlight the trace
      // the highlight styles are defined in the trackLayer constructor
      this.highlight = new OpenLayers.Control.SelectFeature(this.trackLayer,{
	 multiple : false,
	 clickout : false,
	 toggle : false,
	 highlightOnly : true,
      });

      if (this.select){
	 this.map.removeControl(this.select);
      }
      // add a navigation selection feature control
      this.select = new OpenLayers.Control.SelectFeature(this.trackLayer,{
	 multiple : false,
	 clickout : false,
	 toggle : false,
	 highlightOnly : true,
	 onSelect : function(feature){
	    var instance = trackLayer;
	    //triggered by user
	    if (!instance.ignoreSelect){
	       console.log("skipping...");

	       var srcOld = instance.track.getActive().getData("src"),
	           src = feature.geo_data.src,
	           videotimestart = feature.geo_data.videotimestart;

	       //hit a mapconnection do nothing
	       if (!videotimestart){
		  alert("There is no video to show here.");
		  return;
	       }
	       //hit another video. set active and load video
	       else if (srcOld !== src){
		  instance._stopHighlight();
		  instance.track.setActive(src,feature.geo_data.id);
		  instance._startVideo();
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

      
      this.map.addControl(this.highlight);
      this.map.addControl(this.select);
      this.highlight.activate();
      this.select.activate();
   },
};
