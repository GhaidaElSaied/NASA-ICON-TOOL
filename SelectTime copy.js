var clock = new Cesium.Clock({
   startTime : Cesium.JulianDate.fromIso8601("2000-12-25"), //this would be set to the first time we have data
   currentTime : Cesium.JulianDate.fromIso8601("2017-11-15"), //this would be the most current data spot
   stopTime : Cesium.JulianDate.fromIso8601("2050-12-26"), //this would be the end of the predictive data
   clockStep : Cesium.ClockStep.SYSTEM_CLOCK_MULTIPLIER,
   multiplier : 1 // how much time to advance each tick
});

var viewer = new Cesium.Viewer('cesiumContainer', {
    clockViewModel : new Cesium.ClockViewModel(clock)
});

viewer.Timeline.zoomTo(clock.startTime,clock.stopTime);


// The viewModel tracks the state of our mini application.
var viewModel = {
    currentTime: "0000-00-00"
    
};

// Convert the viewModel members into knockout observables.
Cesium.knockout.track(viewModel);

// Bind the viewModel to the DOM elements of the UI that call for it.
var toolbar = document.getElementById('toolbar');
Cesium.knockout.applyBindings(viewModel, toolbar);

// Make the active imagery layer a subscriber of the viewModel.
function subscribeLayerParameter(name) {
    Cesium.knockout.getObservable(viewModel, name).subscribe(
        function(newValue) {
                clock.currentTime = Cesium.JulianDate.fromIso8601(newValue)

            
        }
    );
}
subscribeLayerParameter('currentTime');



