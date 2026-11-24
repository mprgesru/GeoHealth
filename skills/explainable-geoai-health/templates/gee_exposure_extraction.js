// =============================================================================
// Explainable GeoAI for Environmental Health
// Earth Engine exposure extraction — Bangladesh DHS default
// =============================================================================
// What this does
//   1. Loads DHS cluster points from *your own* Earth Engine asset.
//   2. Builds annual PM2.5 (MAIAC AOD), LST, NDVI, and optional O3 composites.
//   3. Buffers urban and rural clusters separately (DHS displacement protocol).
//   4. Extracts cluster means and upazila zonal statistics.
//   5. Exports CSV files to Google Drive.
//
// Before running
//   - Register for DHS access and upload the GE shapefile to your own asset.
//   - Set ASSET_ID below. Never hard-code someone else's asset.
//   - Set the year and the PM2.5 calibration.
//   - Do not export coordinates to a public Drive folder.
// =============================================================================

var CONFIG = {
  year: 2022,
  assetId: 'users/YOUR_USERNAME/BDGE81FL_2022',   // <-- your asset
  adminAssetId: 'users/YOUR_USERNAME/BGD_adm3',   // <-- your upazila layer
  buffers: { urban: 2000, rural: 5000 },          // metres
  pm25: { slope: 120, intercept: 15 },             // PM2.5 = AOD * slope + intercept
  includeOzone: false,
  driveFolder: 'GeoHealth_exports',
  scale: 1000
};

// -----------------------------------------------------------------------------
// 1. DHS clusters
// -----------------------------------------------------------------------------
var dhs = ee.FeatureCollection(CONFIG.assetId);

var start = ee.Date.fromYMD(CONFIG.year, 1, 1);
var end = start.advance(1, 'year');

// -----------------------------------------------------------------------------
// 2. Environmental composites
// -----------------------------------------------------------------------------
// A. PM2.5 from MAIAC AOD (470 nm)
var aod = ee.ImageCollection('MODIS/061/MCD19A2_GRANULES')
  .filterDate(start, end)
  .select('Optical_Depth_047');

// MAIAC stores AOD as scaled integers. Apply 0.001 BEFORE the calibration.
// Without this, PM2.5 lands in the tens of thousands (a common bug).
var annualAod = aod.mean().multiply(0.001);
var pm25 = annualAod
  .multiply(CONFIG.pm25.slope)
  .add(CONFIG.pm25.intercept)
  .rename('pm25_ug');

// B. Land surface temperature (MOD11A2), Kelvin -> Celsius
var lst = ee.ImageCollection('MODIS/061/MOD11A2')
  .filterDate(start, end)
  .select('LST_Day_1km')
  .mean()
  .multiply(0.02)
  .subtract(273.15)
  .rename('temp_mean');

// C. NDVI (MOD13A2)
var ndvi = ee.ImageCollection('MODIS/061/MOD13A2')
  .filterDate(start, end)
  .select('NDVI')
  .mean()
  .multiply(0.0001)
  .rename('ndvi_mean');

// D. Optional ozone (Sentinel-5P OFFL L3)
var exposures = pm25.addBands(lst).addBands(ndvi);
if (CONFIG.includeOzone) {
  var o3 = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_O3')
    .filterDate(start, end)
    .select('O3_column_number_density')
    .mean()
    .rename('o3_mol_m2');
  exposures = exposures.addBands(o3);
}

// -----------------------------------------------------------------------------
// 3. Buffer urban and rural clusters separately
// -----------------------------------------------------------------------------
// DHS displaces urban clusters up to 2 km and rural up to 5 km.
// The field name is URBAN_RURA in the standard GE file.
var urban = dhs.filter(ee.Filter.eq('URBAN_RURA', 'U'));
var rural = dhs.filter(ee.Filter.neq('URBAN_RURA', 'U')); // 'R' or null

var urbanBuffered = urban.map(function (f) {
  return f.buffer(CONFIG.buffers.urban);
});
var ruralBuffered = rural.map(function (f) {
  return f.buffer(CONFIG.buffers.rural);
});
var allBuffered = urbanBuffered.merge(ruralBuffered);

// -----------------------------------------------------------------------------
// 4. Extract cluster means
// -----------------------------------------------------------------------------
var clusterExposures = exposures.reduceRegions({
  collection: allBuffered,
  reducer: ee.Reducer.mean(),
  scale: CONFIG.scale
});

Export.table.toDrive({
  collection: clusterExposures,
  description: 'DHS_' + CONFIG.year + '_cluster_exposures',
  folder: CONFIG.driveFolder,
  fileFormat: 'CSV',
  selectors: ['DHSCLUST', 'URBAN_RURA', 'pm25_ug', 'temp_mean', 'ndvi_mean']
});

// -----------------------------------------------------------------------------
// 5. Upazila zonal statistics (for maps)
// -----------------------------------------------------------------------------
var admin = ee.FeatureCollection(CONFIG.adminAssetId);

var zonalReducer = ee.Reducer.mean().combine({
  reducer2: ee.Reducer.minMax(),
  sharedInputs: true
}).combine({
  reducer2: ee.Reducer.stdDev(),
  sharedInputs: true
});

var adminStats = exposures.reduceRegions({
  collection: admin,
  reducer: zonalReducer,
  scale: CONFIG.scale
});

Export.table.toDrive({
  collection: adminStats,
  description: 'DHS_' + CONFIG.year + '_upazila_exposures',
  folder: CONFIG.driveFolder,
  fileFormat: 'CSV'
});

// -----------------------------------------------------------------------------
// 6. Optional: buffer sensitivity
// -----------------------------------------------------------------------------
// Uncomment to export 1–3 km urban and 3–7 km rural means.
// var sens = [1000, 2000, 3000, 4000, 5000, 6000, 7000];
// sens.forEach(function (b) {
//   var buf = dhs.map(function (f) { return f.buffer(b); });
//   var out = exposures.reduceRegions({
//     collection: buf, reducer: ee.Reducer.mean(), scale: CONFIG.scale
//   });
//   Export.table.toDrive({
//     collection: out,
//     description: 'DHS_' + CONFIG.year + '_buffer_' + b + 'm',
//     folder: CONFIG.driveFolder,
//     fileFormat: 'CSV',
//     selectors: ['DHSCLUST', 'URBAN_RURA', 'pm25_ug', 'temp_mean', 'ndvi_mean']
//   });
// });
