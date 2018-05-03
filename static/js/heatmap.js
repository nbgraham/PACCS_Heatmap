
function showFilteredHeatMap(buildings, building_codes, max_room, min_room, seat) {
    res = getOccInDataFormat(buildings, building_codes, max_room, min_room, seat);

    showHeatMap(res.data, res.ylabels, res.xlabels);
}


function showHeatMap(data, ylabels, xlabels) {
    ///////////////////////////////////////////////////////////////////////////
    //////////////////// Set up and initiate svg containers ///////////////////
    ///////////////////////////////////////////////////////////////////////////


    var margin = {
        top: 150,
        right: 20,
        bottom: 50,
        left: 200
    };

    var titleSpace = 25;

    var width = Math.max(Math.min(window.innerWidth, 1500), 500) - margin.left - margin.right - 20,
        gridSize = width / xlabels.length,
        height = gridSize * (ylabels.length+2);

    width += 50;
    height += 50;

    //SVG container
    d3.select("#heatmap").selectAll("svg").remove();
    var svg = d3.select('#heatmap')
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    //Reset the overall font size
    var newFontSize = width * 62.5 / 900;
    d3.select("html").style("font-size", newFontSize + "%");

    ///////////////////////////////////////////////////////////////////////////
    //////////////////////////// Draw Heatmap /////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////

    //Based on the heatmap example of: http://blockbuilder.org/milroc/7014412

    var valMax = d3.max(data, function(d) {return d.val; });
    var colorScale = d3.scale.linear()
        .domain([0, valMax/2, valMax])
        .range(["#FFFFDD", "#3E9583", "#1F2D86"])
        //.interpolate(d3.interpolateHcl);

    var heatmapWrapper = svg.append("g")
                .attr("class", "heatmapWrapper")
                .attr("transform", "translate(0," + titleSpace + ")");

    var tip = d3.tip()
      .attr('class', 'd3-tip')
      .direction('s')
      .offset([8,0])
      .html(function(d) {
        var c = "";
        var enrollment = ""
        if (d.sections === undefined || d.sections.length == 0) {
            c = "No class"
        } else if (d.sections.length > 1) {
            c = "Multiple sections";
            enrollment = d.sections[0].actual_enrollment;
        } else {
            c = d.sections[0].title;
            enrollment = d.sections[0].actual_enrollment;
        }

        return "<strong>" + c + "</strong><br>" + enrollment + "/" + d.room_cap + " : " + Math.round(enrollment/d.room_cap*100) + "%";
      });

    heatmapWrapper.call(tip);

    var yLabels = heatmapWrapper.selectAll(".yLabel")
        .data(ylabels)
        .enter().append("text")
        .text(function (d) { return d; })
        .attr("x", 0)
        .attr("y", function (d, i) { return i * gridSize; })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
        .attr("class", "yLabel mono axis");

    var xLabels = heatmapWrapper.selectAll(".xLabel")
        .data(xlabels)
        .enter().append("text")
        .text(function(d) { return d; })
        .attr("transform", function(d,i) {return ["rotate(-90) translate(", gridSize * 3, ", ", ((i+1)*gridSize), ")"].join("") })
        .attr("x", 0)
        .attr("y", 0)
        .style("text-anchor", "middle")
        .attr("class", "xLabel mono axis");

    var heatMap = heatmapWrapper.selectAll(".val")
        .data(data)
        .enter().append("rect")
        .attr("x", function(d) { return (d.x - 1) * gridSize; })
        .attr("y", function(d) { return (d.y - 1) * gridSize; })
        .attr("class", "val bordered")
        .attr("width", gridSize)
        .attr("height", gridSize)
        .attr("fill", function(d) { return colorScale(d.val); })
        .on('mouseover', function(d) {
            tip.show(d);
            xLabels[0][d.x-1].style.fill= "red";
            yLabels[0][d.y-1].style.fill= "red";
        })
        .on('mouseout', function(d) {
            tip.hide(d);
            xLabels[0][d.x-1].style.fill= "";
            yLabels[0][d.y-1].style.fill= "";
        });

    //Append title to the top
    svg.append("text")
        .attr("class", "title")
        .attr("x", width/2)
        .attr("y", -90)
        .style("text-anchor", "middle")
        .text("Classroom availability by room and time")
    svg.append("text")
        .attr("class", "subtitle")
        .attr("x", width/2)
        .attr("y", -60)
        .style("text-anchor", "middle")
        .text("OU PACCS | 2017");

    ///////////////////////////////////////////////////////////////////////////
    //////////////// Create the gradient for the legend ///////////////////////
    ///////////////////////////////////////////////////////////////////////////

    //Extra scale since the color scale is interpolated
    var valScale = d3.scale.linear()
        .domain([0, d3.max(data, function(d) {return d.val; })])
        .range([0, width])

    //Calculate the variables for the temp gradient
    var numStops = 10;
    valRange = valScale.domain();
    valRange[2] = valRange[1] - valRange[0];
    valPoint = [];
    for(var i = 0; i < numStops; i++) {
        valPoint.push(i * valRange[2]/(numStops-1) + valRange[0]);
    }//for i

    //Create the gradient
    svg.append("defs")
        .append("linearGradient")
        .attr("id", "legend-traffic")
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "100%").attr("y2", "0%")
        .selectAll("stop")
        .data(d3.range(numStops))
        .enter().append("stop")
        .attr("offset", function(d,i) {
            return valScale( valPoint[i] )/width;
        })
        .attr("stop-color", function(d,i) {
            return colorScale( valPoint[i] );
        });

    ///////////////////////////////////////////////////////////////////////////
    ////////////////////////// Draw the legend ////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////

    var legendWidth = Math.min(width*0.8, 400);
    //Color Legend container
    var legendsvg = svg.append("g")
        .attr("class", "legendWrapper")
        .attr("transform", "translate(" + (width/2) + "," + (gridSize * ylabels.length + 50 + titleSpace) + ")");

    //Draw the Rectangle
    legendsvg.append("rect")
        .attr("class", "legendRect")
        .attr("x", -legendWidth/2)
        .attr("y", 0)
        //.attr("rx", hexRadius*1.25/2)
        .attr("width", legendWidth)
        .attr("height", 10)
        .style("fill", "url(#legend-traffic)");

    //Append title
    legendsvg.append("text")
        .attr("class", "legendTitle")
        .attr("x", 0)
        .attr("y", -10)
        .style("text-anchor", "middle")
        .text("Seat Utilization (if selected)");

    //Set scale for x-axis
    var xScale = d3.scale.linear()
         .range([-legendWidth/2, legendWidth/2])
         .domain([ 0, valMax] );

    //Define x-axis
    var xAxis = d3.svg.axis()
          .orient("bottom")
          .ticks(5)
          //.tickFormat(formatPercent)
          .scale(xScale);

    //Set up X axis
    legendsvg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + (10) + ")")
        .call(xAxis);


    //Append credit at bottom
    svg.append("text")
        .attr("class", "credit")
        .attr("x", width/2)
        .attr("y", gridSize * (days.length+1) + 260)
        .style("text-anchor", "middle")
        .text("Based on Miles McCrocklin's Heatmap block");

}