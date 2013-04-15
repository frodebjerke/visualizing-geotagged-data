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
$.info.get = function (api_name, title, parameters, language) {

  language = (typeof language === 'undefined') ? "de" : language;

  if(api_name == "wikipedia") {
    parameters['url'] = '/info/wikipedia/'+title+'/'+language+'/';
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

$.position = {
    LEFT : 1,
    RIGHT : -1
}

/**
 * Call to add object to the HTML video overlay
 * @author Jan Vorcak <janvor@ifi.uio.no>
 * @param element - element from OSM API to display
 * @param position - 1 for left side, right side otherwise
 */
 var showElementInVideo = function(element, position) {

  var icons;
  if (position == $.position.LEFT) {
      icons = {
        primary: "ui-icon-arrowthick-1-sw",
      }
  } else {
      icons = {
        secondary: "ui-icon-arrowthick-1-se"
      }
  }

  link = $("<a>").attr("href", "#")
  .css("float", (position == $.position.LEFT ? "left" : "right"))
  .html(element.tags.name)
  .attr("data-wikipedia", element.tags.name)
  .attr("title", element.tags.name)
  .button({ icons : icons });

  $("#video-overlay").append(link);
}

/**
 * Clears HTML video overlay
 */
 var clearVideo = function() {
  $("#video-overlay").html("");
}

/*
 * Return true if object is not far away
 */
var isNearby = function(current, element) {

  var r = 0.0009;

  c_lon = current.data.lon;
  c_lat = current.data.lat;
  e_lon = element.lon;
  e_lat = element.lat;

  return Math.abs(c_lon - e_lon) < r && Math.abs(c_lat - e_lat) < r;
}

/*
 * Return $.position.LEFT if objects is on the left side, $.position.RIGHT if 
 * object is on the right side, false otherwise
 */
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

    if (((x[0] <= e[0] && e[0] <= w[0]) || (x[0] >= e[0] && e[0] >= w[0])) && ((x[1] <= e[1] && e[1] <= w[1]) || (x[1] >= e[1] && e[1] >= w[1]))) {
        // we calculate the determinant of matrix CN->, CE->, if it's positive
        // the object is on the right side, if negative it's on the left side
        position = ((n[0]-c[0])*(e[1]-c[1]) - (n[1]-c[1])*(e[0]-c[0])) >= 0;
        return position == true ? $.position.RIGHT : $.position.LEFT;
    } else return false;
}

/*
 * Displays elements inside response object on the video if they are visible
 */
var showPlacesOnVideo = function(current, next, response) {

  clearVideo();

  $.each(response.elements, function(idx, element) {
    position = isInFrontOfMe(current, next, element);
    if(position == $.position.LEFT || position == $.position.RIGHT) {
      showElementInVideo(element, position);
    }
  });

}

/**
 * Displays POI as markers on map. Sets the markers dynamically to the "seen" nodes from the Overpass response.
 * Adds popups to the markers
 */
 var setMarker = function(response) {
   markerLayer.clearMarkers();

   //iterate through the elements (POIs) of the response
   $.each(response.elements, function(idx, element) {

    var text;

    //set the text for additional information (if available)
    $.info.get("wikipedia", element.tags.name, {
     success : function (response) {
      if (response) text = response;
      else text = "No Wikipedia content found."
    },
    error : function (error) {
      text = "No Wikipedia content found.";
    },
  });

    //get the position of the element and transform it into the right projection 
    var lonLat = new OpenLayers.LonLat( element.lon, element.lat ).transform('EPSG:4326', map.getProjectionObject());

    //create a marker
    marker = new OpenLayers.Marker(lonLat);

    //add a mouse listener to the marker and define the event that will be triggered
    //listen for clicks. if clicked: show a popup with the additional information text
    marker.events.register('click', marker, function(evt) {

      popupText = "<h3>"+element.tags.name + "</h3><hr />" + text;
        popup = new OpenLayers.Popup.FramedCloud("popup", lonLat, null, popupText, null, true);
        map.addPopup(popup, true);
      });

    /**
     //possibility to realize a "hover" functionality.
     //seems a little bit unpractical since you trigger many events while you navigate through the map
     *marker.events.register('mouseover', marker, function(evt) {
     *    popup2Text = "<h3>"+element.tags.name + "</h3><hr />" + text;
     *    popup2 = new OpenLayers.Popup.FramedCloud("Popup2", lonLat, null, popup2Text, null, false);
     *    map.addPopup(popup2);
     *  });
     *marker.events.register('mouseout', marker, function(evt) {popup2.hide();});
     */

    //add marker to the layer
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
   var s = parseFloat(lat) - 0.00005,
   n = parseFloat(lat) + 0.00005,
   w = parseFloat(lon) - 0.00005,
   e = parseFloat(lon) + 0.00005;

   // assemble "position block" for the query
   var position = s +","+ w +","+ n +","+ e;	

   // assemble query
   var query ="data=[out:json];node(" + position + ");node(around:500)[\"historic\"];out;";

   // send query to overpass and handle response (-> call further methods)
   $.ajax({
    type : "post",
    url : "http://overpass-api.de/api/interpreter",
    data : query,
    success : function (response) {
         showPlacesOnVideo(current, next, response);
         setMarker(response);

       },
       error : function (error) {
         console.log("Something went wrong!" + error.responseText);
       },
     });


 }
