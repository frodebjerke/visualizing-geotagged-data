/**
 * @public
 * @description Gets called everytime the video proceeds to a new point.
 * @param current: The last point reached
 * @param next: The next point to be reached
 */
function changedPoints (current, next){
   console.dir(current);
   console.dir(next);
   $.ajax({
      method : "post",
      url : "/info",
      data : {
         lat : current.lat,
         lon : current.lon
      },
      success : function (response) {
         console.dir(response);
      },
      error : function (error) {
         console.log("Something went wrong " + error);
      },
   });
}