var viewer = new Cesium.Viewer('cesiumContainer', {
    terrainProviderViewModels : [], //Disable terrain changing
    infoBox : false, //Disable InfoBox widget
    selectionIndicator : false //Disable selection indicator
});

//Enable lighting based on sun/moon positions
viewer.scene.globe.enableLighting = true;

//Use STK World Terrain
viewer.terrainProvider = new Cesium.CesiumTerrainProvider({
    url : 'https://assets.agi.com/stk-terrain/v1/tilesets/world/tiles',
    requestWaterMask : true,
    requestVertexNormals : true
});

//Enable depth testing so things behind the terrain disappear.
viewer.scene.globe.depthTestAgainstTerrain = true;

//Set bounds of our simulation time
var start = Cesium.JulianDate.fromDate(new Date(2017, 9, 1, 0));
var stop = Cesium.JulianDate.addHours(start, 100, new Cesium.JulianDate());

//Make sure viewer is at the desired time.
viewer.clock.startTime = start.clone();
viewer.clock.stopTime = stop.clone();
viewer.clock.currentTime = start.clone();
viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP; //Loop at the end
viewer.clock.multiplier = 10;

//Set timeline to simulation bounds
viewer.timeline.zoomTo(start, stop);

//Generate a random circular pattern with varying heights.
//this should actually take in some kind of data form where maybe it iterates through sets of points? 
function computeOrbit(lon, lat, altitude) {
    var property = new Cesium.SampledPositionProperty();
    for (var i = 0; i <= 86400; i += 4) {
        var time = Cesium.JulianDate.addSeconds(start, i, new Cesium.JulianDate());
        var position = Cesium.Cartesian3.fromDegrees(lon, lat, altitude);
        //obviously this isn't how you would eventually get the lat and long
        var negative = false;
        if (lon == 180) {
            negative = true;
        }
        if (negative){
            lon = lon - .0167;
        } else {
            lon = lon + .0167
        } 
        
        property.addSample(time, position);

        //Also create a point for each sample we generate.
        viewer.entities.add({
            position : position,
            point : {
                pixelSize : .1,
                color : Cesium.Color.TRANSPARENT,
                outlineColor : Cesium.Color.RED,
                outlineWidth :.1
          }
      });
    }
    return property;
}

var position = computeOrbit(0, 0, 1000);