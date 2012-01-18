/* This is the base Steer JavaScript object. There is only ever one of these
 * loaded (referenced as steer with a lower-case h) which happens immediately
 * after the definition below.
 *
 * Scripts that are dependent on functionality defined in the Steer object
 * must be included after this script in templates/base.html.
 */
var Steer = function() {
  var steer = {};
  var initFunctions = [];

  /* Use the addInitFunction() function to add initialization code which must
   * be called on DOM ready. This is useful for adding things like event
   * handlers or any other initialization functions which should preceed user
   * interaction but rely on DOM readiness.
   */
  steer.addInitFunction = function(fn) {
    initFunctions.push(fn);
  };

  /* Call all initialization functions and clear the queue. */
  steer.init = function() {
    $.each(initFunctions, function(ind, fn) {
      fn();
    });

    // Prevent multiple executions, just in case.
    initFunctions = [];
  };

  return steer;
};

// Create the one and only steer object.
var steer = Steer();

// Call init on DOM ready.
$(document).ready(steer.init);
