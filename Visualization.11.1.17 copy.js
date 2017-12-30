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
var stop = Cesium.JulianDate.addHours(start, 24, new Cesium.JulianDate());

//Make sure viewer is at the desired time.
viewer.clock.startTime = start.clone();
viewer.clock.stopTime = stop.clone();
viewer.clock.currentTime = start.clone();
viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP; //Loop at the end
viewer.clock.multiplier = 2500;

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
        /** viewer.entities.add({
            position : position,
            point : {
                pixelSize : .1,
                color : Cesium.Color.TRANSPARENT,
                outlineColor : Cesium.Color.RED,
                outlineWidth :.1
          }
      });
      */
    }
    return property;
}

var position = computeOrbit(0, 0, 1000);


//Actually create the entity
var entity = viewer.entities.add({

    //Set the entity availability to the same interval as the simulation time.
    availability : new Cesium.TimeIntervalCollection([new Cesium.TimeInterval({
        start : start,
        stop : stop
    })]),

    //Use our computed positions
    position : position,

    //Automatically compute orientation based on position movement.
    orientation : new Cesium.VelocityOrientationProperty(position),

    //Load the Cesium plane model to represent the entity
    model : {
        uri : '../../SampleData/models/CesiumAir/Cesium_Air.gltf',
        minimumPixelSize : 64
    },

    //Show the path as a yellow line sampled in 4 second increments.
    path : {
        resolution : 4,
        material : new Cesium.PolylineGlowMaterialProperty({
            glowPower : 0.1,
            color : Cesium.Color.YELLOW
        }),
        leadTime : 0,
        trailTime: 40000 ,
        width : 10
   }

    /**path : new Cesium.PathGraphics({
        leadtime : 0,
        trailtime: 5,
        resolution : 4,
        material : new Cesium.PolylineGlowMaterialProperty({
            glowPower : 0.1,
            color : Cesium.Color.YELLOW
        }),
        width : 10

    }) */
});

//Add button to view the path from the top down
Sandcastle.addToolbarButton('View Top Down', function() {
    viewer.trackedEntity = undefined;
    viewer.zoomTo(viewer.entities, new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-90)));
});

//Add button to view the path from the side
Sandcastle.addToolbarButton('View Side', function() {
    viewer.trackedEntity = undefined;
    viewer.zoomTo(viewer.entities, new Cesium.HeadingPitchRange(Cesium.Math.toRadians(-90), Cesium.Math.toRadians(-15), 7500));
});

//Add button to track the entity as it moves
Sandcastle.addToolbarButton('View Aircraft', function() {
    viewer.trackedEntity = entity;
});



