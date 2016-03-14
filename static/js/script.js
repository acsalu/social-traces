var Service = Object.freeze({FACEBOOK: 0, TWITTER: 1, GITHUB: 2, FOURSQUARE: 3});

function visualize(timestamps, service) {

  var margin = {top: 10, right: 30, bottom: 30, left: 30},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

  var hourFormat = d3.time.format("%H");
  var minuteFormat = d3.time.format("%M");

  var transformer = function(t) {
      return parseInt(hourFormat(new Date(t))) * 60 + parseInt(minuteFormat(new Date(t)));
  }

  var minuteInDay = timestamps.map(transformer);

  var x = d3.scale.linear()
    .domain([0, 24 * 60])
    .range([0, width]);

  var data = d3.layout.histogram()
    .bins(x.ticks(24))
    (minuteInDay);

  var y = d3.scale.linear()
    .domain([0, d3.max(data, function(d) { return d.y; })])
    .range([height, 0]);

  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

  var svg = d3.select('#traces')
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append('g')
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var barClass = "bar";
  switch (service) {
    case Service.FACEBOOK:
      barClass += " fb";
      break;
    case Service.TWITTER:
      barClass += " tw";
      break;
    case Service.GITHUB:
      barClass += " gh";
      break;
    case Service.FOURSQUARE:
      barClass += " fsq";
      break;
    default:
      break;
  }

  var bar = svg.selectAll('.bar')
      .data(data)
    .enter().append('g')
      .attr('class', barClass)
      .attr('transform', function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

  
  bar.append("rect")
    .attr("x", x(data[0].dx) / 4 * service)
    .attr("width", x(data[0].dx) / 4)
    .attr("height", function(d) { return height - y(d.y); });

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

function requestTimestamps() {
  $.getJSON('/fsq_data', function(data) {
    visualize(data, Service.FOURSQUARE);
  });

  $.getJSON('/gh_data', function(data) {
    visualize(data, Service.GITHUB);
  });
}