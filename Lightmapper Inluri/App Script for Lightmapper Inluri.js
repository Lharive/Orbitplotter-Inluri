function resample_data() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Star System Generator");

  var thermalRand = Math.sqrt(Math.random());
  sheet.getRange("C40").setValue(thermalRand);

  var u = Math.random();

  var z = Math.sqrt(-2*Math.log(u))*Math.cos(2 * Math.PI * Math.random());
  var myu = 5;
  var v = 2.3;
  var logN = myu + v * z;
  sheet.getRange("C28").setValue(logN);

}

/* this was the Google Script I used paired with an older version of the Lightmapper Inluri spreadsheet.*/
/* I abandoned this line of work because (a) i do not like Javascript (b) This was overkill (c) It didn't solve the core problems (d) I barely understood any of this code myself*/
