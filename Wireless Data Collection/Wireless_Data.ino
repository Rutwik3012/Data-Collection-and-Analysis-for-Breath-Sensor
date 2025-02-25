#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Update.h>

#define ADC_PIN 34  // Define the ADC pin you're using
const char* host = "MyESP32";
const char* ssid = "Rutwiik";
const char* password = "87654321";

WebServer server(80);

//***************************************************************************************************
/* Style */
String style =
  "<style>"
  /* Style for the background blur */
  ".background {"
  "  position: fixed; "
  "  top: 0; "
  "  left: 0; "
  "  width: 100%; "
  "  height: 100%; "
  "  background: url(https://diat.ac.in/wp-content/uploads/2023/12/DIAT-LOGO12345-e1701673199828.jpg) no-repeat center center fixed; "
  "  background-size: cover; "
  "  filter: blur(8px); "
  "  opacity: 1; "
  "  z-index: -1; " /* Ensures the background stays behind the content */
  "}"

  "#file-input, input { width: 100%; height: 44px; border-radius: 4px; margin: 10px auto; font-size: 15px; }"
  "input { background: #f1f1f1; border: 0; padding: 0 15px; }"

  /* Style for the rest of the content */
  "body { margin: 0; padding: 0; }"
  "form {"
  "  background: rgba(255, 255, 255, 0.8); "  /* Slight transparency to show the background */
  "  max-width: 258px; "
  "  margin: 75px auto; "
  "  padding: 30px; "
  "  border-radius: 5px; "
  "  text-align: center;"
  "  z-index: 1; "
  "  position: relative; "
  "}"
  "#bar, #prgbar { background-color: #f1f1f1; border-radius: 10px; }"
  "#bar { background-color: #3498db; width: 0%; height: 10px; }"
  ".btn {"
  "  background: #3498db; "
  "  color: #fff; "
  "  cursor: pointer; "
  "  margin: 10px 5px; "
  "}"
  "</style>";




/* Login page */
String loginIndex =
  "<form name=loginForm>"
  "<h1>ESP32 Login</h1>"
  "<input name=userid placeholder='User ID'> "
  "<input name=pwd placeholder=Password type=Password> "
  "<input type=submit onclick=check(this.form) class=btn value=Login></form>"
  "<script>"
  "function check(form) {"
  "if(form.userid.value=='diat' && form.pwd.value=='diat')"
  "{window.open('/serverIndex')}"
  "else"
  "{alert('Error Password or Username')}"
  "}"
  "</script>" + style;

/* Server Index Page */
String serverIndex =
  "<style>"
  /* Style for the background blur */
  ".background {"
  "  position: fixed; "
  "  top: 0; "
  "  left: 0; "
  "  width: 100%; "
  "  height: 100%; "
  "  background: url(https://diat.ac.in/wp-content/uploads/2023/12/DIAT-LOGO12345-e1701673199828.jpg) no-repeat center center fixed; "
  "  background-size: cover; "
  "  filter: blur(8px); "
  "  opacity: 1; "
  "  z-index: -1; " /* Ensures the background stays behind the content */
  "}"
  
  "#file-input, input { width: 100%; height: 44px; border-radius: 4px; margin: 10px auto; font-size: 15px; }"
  "input { background: #f1f1f1; border: 0; padding: 0 15px; }"

  /* Style for the rest of the content */
  "body { margin: 0; padding: 0; }"
  "form {"
  "  background: rgba(255, 255, 255, 0.8); "  /* Slight transparency to show the background */
  "  max-width: 258px; "
  "  margin: 75px auto; "
  "  padding: 30px; "
  "  border-radius: 5px; "
  "  text-align: center; "
  "  z-index: 1; "
  "  position: relative; "
  "}"
  "#bar, #prgbar { background-color: #f1f1f1; border-radius: 10px; }"
  "#bar { background-color: #3498db; width: 0%; height: 10px; }"
  ".btn {"
  "  background: #3498db; "
  "  color: #fff; "
  "  cursor: pointer; "
  "  margin: 10px 5px; "
  "}"
  "</style>"
  "<div class='background'></div>"
  "<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js'></script>"
  "<div style='text-align: center; margin-top: 20px;'>"
  "  <button onclick=\"location.href='/startSession'\" class='btn' style='font-weight: bold; font-size: 18px; padding: 10px 20px; margin-right: 10px; background-color: green; color: white; border: none; border-radius: 5px;'>Start Session</button>"
  "  <button onclick=\"location.href='/endSession'\" class='btn' style='font-weight: bold; font-size: 18px; padding: 10px 20px; margin-left: 10px; background-color: red; color: white; border: none; border-radius: 5px;'>End Session</button>"
  "</div>"
  "<br><br>"
  "<script>"
  "function sub(obj){"
  "var fileName = obj.value.split('\\\\');"
  "document.getElementById('file-input').innerHTML = '   '+ fileName[fileName.length-1];"
  "};"
  "$('form').submit(function(e){"
  "e.preventDefault();"
  "var form = $('#upload_form')[0];"
  "var data = new FormData(form);"
  "$.ajax({"
  "url: '/update',"
  "type: 'POST',"
  "data: data,"
  "contentType: false,"
  "processData:false,"
  "xhr: function() {"
  "var xhr = new window.XMLHttpRequest();"
  "xhr.upload.addEventListener('progress', function(evt) {"
  "if (evt.lengthComputable) {"
  "var per = evt.loaded / evt.total;"
  "$('#prg').html('progress: ' + Math.round(per*100) + '%');"
  "$('#bar').css('width',Math.round(per*100) + '%');"
  "} "
  "}, false);"
  "return xhr;"
  "},"
  "success:function(d, s) {"
  "console.log('success!') "
  "},"
  "error: function (a, b, c) {"
  "}"
  "});"
  "});"
  "</script>";


//***************************************************************************************************
// Variable to store ADC values over time
String adcValues = "";

// Function to capture ADC values for 60 seconds, with time tracking from 0 to 60 seconds
void startSession() {
  adcValues = "";  // Clear previous values
  for (int time = 0; time <= 60; time++) {
    int analogValue = analogRead(ADC_PIN);  // Read ADC value
    adcValues +=  String(time) + ", " + String(analogValue) + "\n";
    //adcValues += "Time: " + String(time) + "s, ADC Value: " + String(analogValue) + "\n";
    delay(1000);  // Wait for 1 second before taking the next reading
  }
}

//***************************************************************************************************
// // New functions for End Session
void endSession() {
  adcValues = "";  // Clear ADC values
  server.send(200, "text/plain", "Session ended! ADC values cleared.");
}

//***************************************************************************************************
void setup(void) {
  Serial.begin(115200);

  // Connect to WiFi network.
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection.
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print(">> Connected to ");
  Serial.println(ssid);
  Serial.print(">> IP address: ");
  Serial.println(WiFi.localIP());

  if (!MDNS.begin(host)) {
    Serial.println(">> Error setting up MDNS responder!");
    while (1) {
      delay(1000);
    }
  }
  Serial.println(">> mDNS responder started.");

  server.on("/", HTTP_GET, []() {
  server.sendHeader("Connection", "close");
  server.send(200, "text/html", "<div class='background'></div>" + loginIndex);
});

  server.on("/serverIndex", HTTP_GET, []() {
    server.sendHeader("Connection", "close");
    server.send(200, "text/html", serverIndex);
  });

  // Endpoint to get ADC values
  server.on("/startSession", HTTP_GET, []() {
    startSession();  // Collect ADC values for 60 seconds
    server.send(200, "text/plain", adcValues);  // Send the captured ADC values to the browser
  });

  // New endpoints for End Session
  server.on("/endSession", HTTP_GET, endSession);

  server.begin();
}

//***************************************************************************************************
void loop(void) {
  server.handleClient();
}

