
$( function() {
$( "#tabs" ).tabs({
  event: "mouseover"
});
} );


$(document).ready(function() {    
      var x = new Array();
      var y = new Array();
      var trace;
      var layout;
      
      namespace = '/test';
      var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

      socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!', value: 1}); });

      socket.on('my_response', function(msg) {
        $('#json_response').append('JSON response: '+': '+JSON.stringify(msg.data, null,2)+'<br>').html; 
        //graphData = JSON.parse(msg.data)
        console.log(msg)
        //console.log(msg.data);
        //$('#log').append('Received #'+msg.count+': '+msg.data+'<br>').html(); 
        x.push(parseFloat(msg.count));
        y.push(parseFloat(msg.data.y));
        trace = {
            x: x,
            y: y,
        };       
        layout = {
          title: 'Data',
          xaxis: {
              title: 'x',
          },
          yaxis: {
              title: 'y',
              //range: [-1,1]
          }
        };
        //console.log(trace);
        var traces = new Array();
        traces.push(trace);
        Plotly.newPlot($('#plotdiv')[0], traces, layout); 
        //addTraces               
        });

      $('form#emit').submit(function(event) {
          socket.emit('my_event', {value: $('#emit_value').val()});
          return false; });
      $('#buttonVal').click(function(event) {
          //console.log($('#buttonVal').val());
          socket.emit('click_event', {value: $('#buttonVal').val()});
          return false; });
      $('form#disconnect').submit(function(event) {
          socket.emit('disconnect_request');
          return false; });         
      });
      
      
      $(document).ready(function() {    
      var gauge = new RadialGauge({
          renderTo: 'canvasID',
          width: 300,
          height: 300,
          units: "Km/h",
          minValue: -1,
          maxValue: 1,
          majorTicks: [
              "-1.0",
              "-0.9",
              "-0.8",
              "-0.7",
              "-0.6",
              "-0.5",
              "-0.4",
              "-0.3",
              "-0.2",
              "-0.1",
              "0",
              "0.1",
              "0.2",
              "0.3",
              "0.4",
              "0.5",
              "0.6",
              "0.7",
              "0.8",
              "0.9",
              "1.0"
          ],
          minorTicks: 2,
          strokeTicks: true,
          highlights: [
              {
                  "from": 0.5,
                  "to": 1,
                  "color": "rgba(200, 50, 50, .75)"
              }
          ],
          colorPlate: "#fff",
          borderShadowWidth: 0,
          borders: false,
          needleType: "arrow",
          needleWidth: 2,
          needleCircleSize: 7,
          needleCircleOuter: true,
          needleCircleInner: false,
          animationDuration: 1500,
          animationRule: "linear"
      });
      gauge.draw();
      gauge.value = "0";

      
      namespace = '/test';
      var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

      socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!', value: 1}); });

      socket.on('my_response', function(msg) {
        console.log(msg.data);
        $('#log').append('Received #'+msg.count+': '+msg.data+'<br>').html(); 
        gauge.value = msg.data.y;                
        });

      $('form#emit').submit(function(event) {
          socket.emit('my_event', {value: $('#emit_value').val()});
          return false; });
      $('#buttonVal').click(function(event) {
          //console.log($('#buttonVal').val());
          socket.emit('click_event', {value: $('#buttonVal').val()});
          return false; });
      $('form#disconnect').submit(function(event) {
          socket.emit('disconnect_request');
          return false; });         
      });
