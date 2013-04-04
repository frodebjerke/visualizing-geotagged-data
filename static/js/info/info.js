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
/*
$(function() {
  $(document).tooltip({
    items : "[data-wikipedia]",
    content : function () {
        return $(this).attr("data-wikipedia");
    }
  });
});
*/

/**
 * Call to add object to the HTML video overlay
 * @author Jan Vorcak <janvor@ifi.uio.no>
 * @param text - text to be displayed
 * @param left - left position in px
 * @param top_ - top position in px
 */
var showElementInVideo = function(element, left, top_) {
    link = $("<a>").attr("href", "#")
        .css("left", left+"px")
        .css("top", top_+"px")
        .html(element.tags.name)
        .attr("data-wikipedia", element.tags.name)
        .attr("title", element.tags.name);

    $("#video-overlay").append(link);
}

/**
 * Clears HTML video overlay
 */
var clearVideo = function() {
    $("#video-overlay").html("");
}

var isNearby = function(current, element) {

    var r = 0.0009;

    c_lon = current.data.lon;
    c_lat = current.data.lat;
    e_lon = element.lon;
    e_lat = element.lat;

    return Math.abs(c_lon - e_lon) < r && Math.abs(c_lat - e_lat) < r;
}

var isInFrontOfMe = function(current, next, element) {

    // if one of the following is null, it's not worth of counting
    if(!(current && next)) return false;

    // prepare points
    var x = {};
    var y = {};
    var z = {};
    var w = {};
    var c = {};
    var n = {};

    var e = {}; // element

    // prepare vectors
    var v1 = {};
    var v2 = {};

    // get the coordinates - [0] = lat, [1] = lon
    c[0] = parseFloat(current.data.lat);
    c[1] = parseFloat(current.data.lon);
    n[0] = parseFloat(next.data.lat);
    n[1] = parseFloat(next.data.lon);
    e[0] = parseFloat(element.lat);
    e[1] = parseFloat(element.lon);

    // count the vector v1 = (C,N)
    v1[0] = n[0] - c[0];
    v1[1] = n[1] - c[1];

    // count it's normal vector
    v2[0] = -v1[1]
    v2[1] =  v1[0]

    //        ->
    //        v2
    // Z ---- N ---- W
    //        |
    //        |->
    //        |v1
    //        |
    //        |
    // X      C      Y

    // x should be C + v2 vector
    x[0] = c[0] - v2[0];
    x[1] = c[1] - v2[1];

    // z should be N + v2 vector
    z[0] = n[0] - v2[0];
    z[1] = n[1] - v2[1];

    // we add the reversed v2 vector
    y[0] = c[0] + v2[0];
    y[1] = c[1] + v2[1];

    // we add the reversed v2 vector
    w[0] = n[0] + v2[0];
    w[1] = n[1] + v2[1];

    return (((x[0] <= e[0] && e[0] <= w[0]) || (x[0] >= e[0] && e[0] >= w[0])) && ((x[1] <= e[1] && e[1] <= w[1]) || (x[1] >= e[1] && e[1] >= w[1])));
}

var showPlacesOnVideo = function(current, next, response) {
    clearVideo();

    $.each(response.elements, function(idx, element) {
        if(isInFrontOfMe(current, next, element)) {
            showElementInVideo(element);
        }
    });
}

/**
 * Displays POI as markers on map. Sets the markers dynamically to the "seen" nodes from the Overpass response.
 * Adds popups to the markers
 */
var setMarker = function(response) {
   markerLayer.clearMarkers();

   $.each(response.elements, function(idx, element) {

      var text;
	
      $.info.get("wikipedia", element.tags.name, {
         success : function (response) {
            text = response;
         },
         error : function (error) {
            text = "no additional information";
         },
      });

      var lonLat = new OpenLayers.LonLat( element.lon, element.lat ).transform('EPSG:4326', map.getProjectionObject());
      
      marker = new OpenLayers.Marker(lonLat);
      marker.events.register('mouseover', marker, function(evt) {
         popup = new OpenLayers.Popup.FramedCloud("Popup", lonLat, null, element.tags.name + "<br>" + text, null, false);
         map.addPopup(popup);
      });

      marker.events.register('mouseout', marker, function(evt) {popup.hide();});

      marker.events.register('click', marker, function(evt) {
         //Put your code here for the onClick-behaviour or call a method
         console.log("click!");
      });

      markerLayer.addMarker(marker);
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
   var s = lat, //parseFloat(lat) - 0.00005,
       n = lat, //parseFloat(lat) + 0.00005,
       w = lon, //parseFloat(lon) - 0.00005,
       e = lon; //parseFloat(lon) + 0.00005;

   /**
   Bounding Box example
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
   */
   
   
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
         //console.dir(response);
         showPlacesOnVideo(current, next, response);
         setMarker(response);
      },
      error : function (error) {
         console.log("Something went wrong!" + error.responseText);
      },
   });

  
}

