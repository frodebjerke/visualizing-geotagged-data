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


   if (src === null) {
      // you might want to do nothing here because there is no video to show here (=MapPointConnection)
   }

   // retrieve rich information from an external source
   // the controller currently resides in info/views.py
   // currently django will complain about a missing csrf token for whatever reason
   $.ajax({
      type : "post",
      url : "/info/",
      data : {
         lat : lat,
         lon : lon
      },
      success : function (response) {
         console.dir(response);
      },
      error : function (error) {
         console.log("Something went wrong!" + error.responseText);
      },
   });
}