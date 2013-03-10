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
