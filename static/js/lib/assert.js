"use strict";


function croak (actual, expected, message) {
   if (message) {
      throw new Error(message);
   } else {
      throw new Error(actual + " is not " + expected + "!");
   }
}

function assert (actual, expected, message) {
   if (actual !== expected) {
      croak(actual, expected, message);
   }
}

function assertTrue (actual, message) {
   if (actual !== true) {
      croak(actual, true, message);
   }
}

function assertNumber(actual, message) {
   if (typeof actual !== "number") {
      croak(typeof actual, "number", message);
   }
}