/*global $, OpenLayers, styles, geographic, spherical, OpenLayers, toVectors, $map, assertTrue, TrackLayer, assert*/

"use strict";


/**
 * @public
 * @author Frederik Claus <f.v.claus@googlemail.com>
 * @description Wraps all OSM related functionality like managing select controls.
 * @param {OpenLayers.Map} map
 * @param {TrackLayer} track
 */
var MapLayer = function(map,track){
   assert(map.CLASS_NAME, "OpenLayers.Map");
   assertTrue(track instanceof TrackLayer);

   this.map = map;
   this.mode = null;
   this.track = track;
};

MapLayer.prototype = {
   /**
    * @public
    * @description Adds a new layer with selection features to the map. Will reinitialise if called more than once.
    */
   init : function(){
      assertTrue(typeof styles.default === "object");
      assertTrue(typeof styles.selected === "object");
      
      if (this.layer){
	 this.map.removeLayer(this.layer);
      }
      this.layer = new OpenLayers.Layer.Vector("Full Track",  {
	 styleMap : new OpenLayers.StyleMap({
	    "default" : styles.default, // default styles highlights the graph
	    "select" : styles.selected // selected styles highlights nodes selected by the user and the shortest trace selected by the alogrithm
	 }),
	 projection: geographic
      });

      this._initControls();
   },

   /**
    * @public 
    * @description Updates the map to display the new graph
    * @param {int} mode One of the allowed modes of the graph
    */
   update : function(mode){
      assertTrue(typeof mode === "number");

      var instance = this;
      this.init();
      
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
	       var vectors = toVectors(pair);
	       instance.layer.addFeatures(vectors);		
	    });
	    instance.map.addLayer(instance.layer);
	    var center = instance.getCenter();

	    instance.map.setCenter(center, // Center of the map
    			           15 // Zoom level
    			          );

	    $map.trigger("updateStop.geo");
	 }
      });
   },
   /**
    * @public
    * @description This does not work all the time right now.
    */
   resetSelectedFeatures : function(){
      //TODO sometimes this does not work
      this.select.unselectAll();
   },
   //select listener for point select
   onSelect : function(){
      assertTrue(this instanceof MapLayer);

      var instance = this,
          selectedFeatures = this.layer.selectedFeatures,
	  length = selectedFeatures.length,
          source = null,
          target = null;
      
      if (length > 2){
	 alert("Select only two points. Please reload the page if you cannot completely reset your selection. This is a bug.");
      } else if (length > 1){
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
	       "mode" : this.getMode(),
	       "source" : source,
	       "target" : target
	    },
	    dataType : "json",
	    success : function(points){
	       if (points.length === 0){
		  alert("No connection beetween the two points.");
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
   },
   /**
    * @public
    * @returns null if mode is undefined
    */
   getMode : function(){
      return this.mode;
   },
   /**
    * @public
    * @returns null if instance not initialiased
    */
   getCenter : function(){
      //gets the center from the bounding box that holds all layer features
      var extent = this.layer.getDataExtent();
      if (extent){
	 return extent.getCenterLonLat();
      }
      return null;
   },
   /**
    * @private
    */
   _initControls : function(){
      //init function remove control first and then add it again
      this._initSnap();
      this._initSelect();
      this._initPointSelect();
   },
   /**
    * @private
    */
   _initSnap : function(){
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
	       var point = event.point;
	       point = point.transform(spherical,geographic);

	    },
	 }
      });
      this.map.addControl(this.snap);
      this.snap.activate();
   },
   /**
    * @private
    * @description highlight only select
    */
   _initSelect : function(){
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
   /**
    * @private
    * @description tracklayer point selection
    */
   _initPointSelect : function(){
      var instance = this;

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
         // wrap in function to apply 'this'
	 onSelect : function () {
            // instance.onSelect.apply(instance);
            instance.onSelect();
         },
      });
      this.map.addControl(this.pointSelect);
      this.pointSelect.activate();
   }
   //TODO the graph layer does not need to be disabled, because the tracelayer will completely cover it
   // /**
   //  * @public
   //  * @description Disables all interactive features
   //  */
   // disableControls : function(){
   //    this.pointSelect.deactivate();
   //    this.select.deactivate();
   // },
   // /**
   //  * @private
   //  * @description Enables all interactive features
   //  */
   // enableControls : function(){
   //    this.pointSelect.activate();
   //    this.select.activate();
   // },
};



    

