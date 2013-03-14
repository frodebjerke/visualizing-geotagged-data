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
var displayOnVideo = function(text, left, top_) {
    $("#video-overlay").append("<a href='#' style='left:"+left+"px;top:"+top_+"px'>"+text+"</a>");
}

/**
 * Clears HTML video overlay
 */
var clearVideo = function() {
    $("#video-overlay").html("");
}

/**
 * @public
 * @description Gets called everytime the video proceeds to a new point on the map.
 * @param {TrackPoint or TrackConnection} current: The last point reached
 * @param {TrackPoint or TrackConnection} next: The next point to be reached
 */
function onVideoProgress (current, next){
   // I will add some more documentation once I now what the other methods of the TrackPoint/TrackPointConnection where there for ;)
   console.log("Video reached new Point!");
   console.dir(current);
   console.dir(next);

   // use getData() to retrieve the lat/lon and video src
   var lat = next.getData("lat"),
       lon = next.getData("lon"),
       src = next.getData("src");

   // calulate points for the bounding box of overpass api
   var s = parseFloat(lat) - 0.00005,
       n = parseFloat(lat) + 0.00005,
       w = parseFloat(lon) - 0.00005,
       e = parseFloat(lon) + 0.00005;
   
   // assemble "position block" for the query
   var position = s +","+ w +","+ n +","+ e;	

   // assemble query
   var query ="data=[out:json];node(" + position + ");node(around:500)[\"historic\"];out;";



   if (src === null) {
      // you might want to do nothing here because there is no video to show here (=MapPointConnection)
   }

   // send query to overpass and handle response
   $.ajax({
      type : "post",
      url : "http://overpass-api.de/api/interpreter",
      data : query,
      success : function (response) {
         console.dir(response);
      },
      error : function (error) {
         console.log("Something went wrong!" + error.responseText);
      },
   });
}

