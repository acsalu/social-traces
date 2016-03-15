function requestTimestamps() {
  $.getJSON('/fb_data', function(data) {
    activities[Service.FACEBOOK] = data;
    $('.btn-facebook+p').html(data.length + " Posts").show();
    visualize();
  });

  $.getJSON('/ig_data', function(data) {
    activities[Service.INSTAGRAM] = data;
    var stats = 
    $('.btn-instagram+p').html(data.length + " Photos").show();
    visualize();
  });

  $.getJSON('/gh_data', function(data) {
    activities[Service.GITHUB] = data;
    $('.btn-github+p').html(data.length + " Events").show();
    visualize();
  });

  $.getJSON('/fsq_data', function(data) {
    activities[Service.FOURSQUARE] = data;
    $('.btn-foursquare+p').html(data.length + " Check-ins").show();
    visualize();
  });
}

var Service = Object.freeze({FACEBOOK: 0, INSTAGRAM: 1, GITHUB: 2, FOURSQUARE: 3});
var className = {};
className[Service.FACEBOOK] = 'fb';
className[Service.INSTAGRAM] = 'ig';
className[Service.GITHUB] = 'gh';
className[Service.FOURSQUARE] = 'fsq';

var activities = {}

var hourFormat = d3.time.format("%H");
var minuteFormat = d3.time.format("%M");

function timestampsToMinuteInDay(t) {
  return parseInt(hourFormat(new Date(t))) * 60 + parseInt(minuteFormat(new Date(t)));
}

function visualize() {

  var margin = {top: 20, right: 20, bottom: 30, left: 20},
    width = 1000 - margin.left - margin.right,
    height = 450 - margin.top - margin.bottom;

  var svg = d3.select('#traces')
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
    .append('g')
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var x = d3.scale.linear()
    .domain([0, 24 * 60])
    .range([0, width]);

  var ticks = [];
  for(var i = 0; i <= 2400; i += 120){
    ticks.push(i);
  }
  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickValues(ticks)
    .tickFormat(function(x){return d3.round(x/60)+":00"});

  var bins = {};

  for (service in activities) {

    var minuteInDay = activities[service];

    var data = d3.layout.histogram()
      .bins(x.ticks(24))
      (minuteInDay);

    bins[service] = data;
  }

  var allBins = []
  for (service in activities) {
    allBins = allBins.concat(bins[service]);
  }

  var y = d3.scale.linear()
    .domain([0, d3.max(allBins, function(d) { return d.y; })])
    .range([height, 0]);

  for (service in activities) {

    if (service in bins) {
      var data = bins[service];

      var bar = svg.selectAll('.' + className[service])
          .data(data)
        .enter().append('g')
          .attr('class', 'bar ' + className[service])
          .attr('transform', function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

      
      bar.append("rect")
        .attr("x", x(data[0].dx) / 4 * service)
        .attr("width", x(data[0].dx) / 4)
        .attr("height", function(d) { return height - y(d.y); });
    }
  }

  // bar.append("text")
  //   .attr("dy", ".75em")
  //   .attr("y", 6)
  //   .attr("x", x(data[0].dx) / 2)
  //   .attr("text-anchor", "middle")
  //   .text(function(d) { return d.y; });

  svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);
}

$(function() {
  $('#fb-login-btn').click(function() {
    FB.login(function(response){
      console.log(response.authResponse.accessToken);
      $.get( '/fb_login', {'access_token': response.authResponse.accessToken } )
      .done(function() {
        window.location.replace('/');
      });
    }, {scope: 'user_posts,user_likes'});
  });
});