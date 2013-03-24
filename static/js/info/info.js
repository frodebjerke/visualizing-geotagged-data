$.info = {};

/**
 * Interface to provide you with the external information about the given object
 * @author Jan Vorcak <janvor@ifi.uio.no>
 * @param api_name - name of the API (for now we support wikipedia)
 * @param parameters - parameters for the ajax request
 *
 * i.e
 * $.info.get("wikipedia", "Oslo Opera", {
      success : function (response) {
         console.dir(response);
      },
      error : function (error) {
         console.log("Something went wrong!" + error.responseText);
      },
   });
 */
$.info.get = function (api_name, title, parameters) {
    if(api_name == "wikipedia") {
        parameters['url'] = '/info/wikipedia/'+title+'/';
        $.ajax(parameters);
    } // here we will be able to add support for other API
};

/**
 * Call to add object to the HTML video overlay
 * @author Jan Vorcak <janvor@ifi.uio.no>
 * @param text - text to be displayed
 * @param left - left position in px
 * @param top_ - top position in px
 */
var showElementInVideo = function(element, left, top_) {
    $("#video-overlay").append("<a href='#' style='left:"+left+"px;top:"+top_+"px'>"+
        element.tags.name+"</a>");
}

/**
 * Clears HTML video overlay
 */
var clearVideo = function() {
    $("#video-overlay").html("");
}

var showPlacesOnVideo = function(response) {
    clearVideo();
    $.each(response.elements, function(idx, element) {
        showElementInVideo(element);
        return false; // for now display just one place, we will need to invent filters
    });
}

/**
 * Displays POI as markers on map. Sets the markers dynamically to the "seen" nodes from the Overpass response.
 */
var setMarker = function(response) {
   markerLayer.clearMarkers();
	
   $.each(response.elements, function(idx, element) {
      //console.log(element);
      var lonLat = new OpenLayers.LonLat( element.lon, element.lat ).transform('EPSG:4326', map.getProjectionObject());
      markerLayer.addMarker(new OpenLayers.Marker(lonLat));
   }); 
}

/**
 * @public
 * @description Gets called everytime the video proceeds to a new point on the map.
 * @param {TrackPoint or TrackConnection} current: The last point reached
 * @param {TrackPoint or TrackConnection} next: The next point to be reached
 */
function onVideoProgress (current, next){

   console.log("Video reached new Point!");
   console.dir(current);
   console.dir(next);

   // the transition is either point -> connection, connection to point, point to point or ended
   pointToConnection = current instanceof TrackPoint && next instanceof TrackConnection,
   connectionToPoint = current instanceof TrackConnection && next instanceof TrackPoint,
   segmentChange = current instanceof TrackPoint && next instanceof TrackPoint,
   ended = current instanceof TrackPoint && next === null;
   
   assertTrue(pointToConnection || connectionToPoint || segmentChange || ended);

   if (ended) {
      console.log("Reached end of track");
      return;
   }

   if (!segmentChange) {
      var connection = (current instanceof TrackConnection)? current : next;
      var source = connection.getData("source");
      console.log("Connection started at %s,%s", source.lat, source.lon);
   } else {
      console.log("This will be skipped, because there is no video to show.");
      return;
   }

   // use getData() to retrieve the lat/lon and video src
   var lat = current.getData("lat"),
       lon = current.getData("lon"),
       src = current.getData("src");

   // calulate points for the bounding box of overpass api
   var s = parseFloat(lat) - 0.00005,
       n = parseFloat(lat) + 0.00005,
       w = parseFloat(lon) - 0.00005,
       e = parseFloat(lon) + 0.00005;



   // get the trace layer
   // @see http://dev.openlayers.org/releases/OpenLayers-2.12/doc/apidocs/files/OpenLayers/Layer/Vector-js.html
   // @see geo.js for the public interface
   var traceLayer = geo.getTraceLayer();
   assert(traceLayer.CLASS_NAME, "OpenLayers.Layer.Vector");
   // calculate the coordinates for the box that covers the area between the current & the next feature
   // this only works on a s->n or n->s trace, not on a w<->e trace
   var currentPoint = geo.toPoint(current.getData("lat") , current.getData("lon")),
       nextPoint = geo.toPoint(next.getData("lat"), next.getData("lon"));
   // draw the bounding box. @see http://dev.openlayers.org/releases/OpenLayers-2.12/doc/apidocs/files/OpenLayers/BaseTypes/Bounds-js.html#OpenLayers.Bounds.OpenLayers.Bounds
   bounds = new OpenLayers.Bounds();
   // use a helper functions to create a OpenLayers.Geometry.Point and wrap the point in a OpenLayers.Feature.Vector
   // if you want to display something else don't forget to transform all points from geographic to spherical projection
   bounds.extend(currentPoint);
   bounds.extend(nextPoint);
   // you can set the style of the feature that will get precedence over the layer style
   // @see http://dev.openlayers.org/releases/OpenLayers-2.12/doc/apidocs/files/OpenLayers/Feature/Vector-js.html#OpenLayers.Feature.Vector.OpenLayers.Feature.Vector
   boundingBox = new OpenLayers.Feature.Vector(bounds.toGeometry(), 
                                               null, 
                                               styles.boundingBox); // styles.boundingBox is defined in styles.js
   // add the feature to the layer. it will get displayed automatically
   traceLayer.addFeatures([boundingBox]);

   
   
   // assemble "position block" for the query
   var position = s +","+ w +","+ n +","+ e;	

   // assemble query
   var query ="data=[out:json];node(" + position + ");node(around:500)[\"historic\"];out;";

   // send query to overpass and handle response
   $.ajax({
      type : "post",
      url : "http://overpass-api.de/api/interpreter",
      data : query,
      success : function (response) {
         console.dir(response);
         showPlacesOnVideo(response);
         setMarker(response);
      },
      error : function (error) {
         console.log("Something went wrong!" + error.responseText);
      },
   });

  
}

