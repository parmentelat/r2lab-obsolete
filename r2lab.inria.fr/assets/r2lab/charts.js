// -*- js-indent-level:4 -*-

/* for eslint */
/*global $ _ moment */   /* _ is from underscore.js */
/*global simpleheat */   /* from Chart.Heat.js */
/*global Chart */        /* from charts.js */
/*global getCookie */    /* from xhttp-django.js */

"use strict"; 

$(document).ready(function() {
    let now = moment();
    let sharedData = null


    let draw = function(data, max) {
	let heat = simpleheat('heat').data(data).max(max);
	//heat.radius(40, 35);//really round
	heat.radius(50, 45);
	// set gradient colors as {0.4: 'blue', 0.65: 'lime', 1: 'red'}
	// heat.gradient({0.4: 'blue', 0.65: 'lime', 1: 'red'});
	let minOpacity = 0.01;
	heat.draw(minOpacity);
    }


    let set_data = function(data) {
	sharedData = data;
    }


    let get_data = function() {
	return sharedData;
    }


    let map_node = function() {
	let map = [];
	let c = [38, 125, 210, 298, 383, 470, 557, 642, 729]; //columns
	let l = [45, 150, 255, 360, 463]; //lines
	let n = 0; //node
	//ignoring holes in a square map [col, line]
	let holes = ['3,1', '3,4', '4,4', '5,1', '5,4', '8,0', '8,1', '8,2'];
	$.each(c, function (cc, vc) {
	    $.each(l, function (ll, vl) {
		n++;
		$.inArray(String(cc+','+ll), holes) > -1 ? n-- : map.push({'id': n, 'c': vc, 'l': vl});
	    });
	});
	return map;
    }


    let is_last_week = function(week_ago) { return (week_ago == 1); }


    let serie_color = function(week) {
	let l_color = ['rgba(243,39,26,.7)', 'rgba(31, 54, 177, 0.7)',
		       'rgba(194,111,225,.7)', 'rgba(13,113,75,.7)',
		       'rgba(158,196,16,.7)', 'rgba(28, 255, 0, 0.7)']; //zero color is for complete series
	let b_color = ['rgba(243,39,26,.6)', 'rgba(31, 54, 177, 0.6)',
		       'rgba(194,111,225,.6)', 'rgba(13,113,75,.6)',
		       'rgba(158,196,16,.6)', 'rgba(28, 255, 0, 0.6)']; //zero color is for complete series

	if(week){
	    try {
		return [b_color[week], l_color[week]];
	    } catch (e) {
		let color = randomColor();

		return [color, color];
	    } 
	}
	else{
	    return [b_color[0], l_color[0]];
	}
    }


    let build_heat_chart = function(data) {
	let val = new Array(38).fill(0);
	$.each(data, function (index, value) {
	    $.each(value['data'], function (i/*, v*/) {
		val[i] = val[i] + 1;
	    });
	});
	let max = Math.max.apply(Math, val);

	data = [];
	let map = map_node();
	$.each(map, function (i, v) {
	    data.push([ v['c'], v['l'], val[v['id']] ]); //[[c[1],l[1], 1], ... or [col pos, lin pos, value]
	});
	draw(data, max);
    }


    let build_line_and_doug_chart = function(data) {
	let w_ago  = [1,2,3,4]; //ex.: 3 means four weeks ago
	let start  = null;
	let end    = null;
	let d_range= [];
	let title  = '';
	let color  = '';
	let xax    = range(0,37); //all nodes
	let val    = null; //ignoring 0 position of the array
	let dataset= {};

	let chartData = {
            labels: xax,
            datasets: []
	};

	$.each(w_ago, function (index, value) {
	    start   = moment().subtract((value    * 7)-1, 'days');
	    end     = moment().subtract((value-1) * 7,    'days');
	    d_range = selectInterval(data, start, end);
	    title   = is_last_week(value) ? value + ' week' : value + ' weeks';
	    color   = serie_color(value);

	    dataset = {
		fill: true,
		borderWidth: 1.7,
		label: title,
		hidden: false,
		backgroundColor: color[0],
		borderColor: color[1],
		data: [],
	    }

	    // select data and sum the ocurences of issues at each node
	    val = new Array(38).fill(0);
	    $.each(d_range, function (index, value) {
		$.each(value['data'], function (i/*, v*/) {
		    val[i] = val[i] + 1;
		});
	    });
	    dataset.data = val;
	    chartData.datasets.push(dataset);
	})

	in_cumulative(chartData);

	//After all dataseries, insert the complete one
	color   = serie_color();
	dataset = {
	    fill: true,
	    borderWidth: 1.7,
	    label: 'all serie',
	    hidden: false,
	    backgroundColor: color[0],
	    borderColor: color[1],
	    data: [],
	}
	start   = now;
	end     = moment('2016-01-01');
	d_range = selectInterval(data, start, end);
	val = new Array(38).fill(0);
	$.each(data, function (index, value) {
	    $.each(value['data'], function (i/*, v*/) {
		val[i] = val[i] + 1;
	    });
	});
	dataset.data = val;
	chartData.datasets.push(dataset);
	//-----------------------------------------------
	set_data(chartData);
	create_line_chart(chartData);
	create_doug_chart(data);
    }


    let in_cumulative = function(chartData) {
	//cumulative values to see difference between weeks
	$.each(chartData.datasets, function (index/*, value*/) {
	    if(index > 0){
		$.each(chartData.datasets[index].data, function (i/*, v*/) {
		    chartData.datasets[index].data[i] =
			chartData.datasets[index].data[i]
			+ chartData.datasets[index-1].data[i]
		});
	    }
	});
	return chartData;
    }


    let parse_each_type_issue = function(data, node) {
	let t=0; let l=0; let z=0;
	$.each(data, function (index, value) {
	    try {
		if(value['data'][node]['t'])//t = start
		    t++;
	    } catch (e) {
		undefined; /* to please eslint */
	    } 
	    try {
		if(value['data'][node]['l'])//l = load
		    l++;
	    } catch (e) {
		undefined; /* to please eslint */
	    } 
	    try {
		if(value['data'][node]['z'])//z = zombie
		    z++;
	    } catch (e) {
		undefined; /* to please eslint */
	    } 
	});
	if (t+l+z == 0) {
	    return [t,l,z,100];
	} else {
	    return [t,l,z,0];
	}
    }


    let customTooltips = function(tooltip) {
	// Tooltip Element
	let tooltipEl = $('#line-chart-tooltip');
	// Hide if no tooltip
	if (!tooltip.opacity) {
            tooltipEl.css({
		opacity: 0
            });
            return;
	}

	//building new tootipe infos
	//============================
	let data = get_data();
	let values = [];
	$.each(data.datasets, function (index, value) {
            values.push(value['data'][tooltip.title]);
	});
	if (tooltip.body) {
            let header = "<div class=\"headerboxtootip\">node "+tooltip.title+"<hr></div>"
            let innerHtml = [header];
            $.each(values, function (index, value) {
		let diff = 0;
		let label = data.datasets[index].label;
		let bcolor = data.datasets[index].backgroundColor;

		if(index > 0){
		    label = label+'&nbsp;: ';
		    diff = values[index] - values[index-1];
		} else {
		    label = label+'&nbsp;&nbsp;&nbsp;: ';
		}

		if(diff > 0)
		    diff = ' (+'+diff+')';
		else if(diff > 0)
		    diff = ' ('+diff+')';
		else
		    diff = '';

		let box = "<div class='box' style='background-color:"
		    + bcolor + "; display:inline'></div>&nbsp;"
		innerHtml.push(box + label + value + diff +'<br>');
            });

            tooltipEl.html(innerHtml);
	}
	//============================

	let posx = tooltip.x + 50;
	let posy = tooltip.y - 100;
	// Display, position, and set styles for font
	tooltipEl.css({
            opacity: 1.5,
            width: tooltip.width ? (tooltip.width + 'px') : 'auto',
            left: posx + 'px',
            top:  posy + 'px',
            fontFamily: tooltip._fontFamily,
            fontSize: 11,
            fontStyle: tooltip._fontStyle,
            padding: tooltip.yPadding + 'px ' + tooltip.xPadding + 'px',
	});

    }


    let create_line_chart = function(chartData) {
	//CREATING LINE CHART
	let ctx = document.getElementById("line").getContext("2d");
	window.myLine = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
		tooltips: {
		    enabled: false,
		    custom: customTooltips
		},
		elements: {
                    rectangle: {
			borderWidth: 0,
			borderSkipped: 'bottom'
                    }
		},
		responsive: true,
		legend: {
                    position: 'right',
		},
		title: {
                    display: true,
                    text: 'issues found "n" weeks ago from today',
                    fontSize: 16,
                    fontStyle: 'normal',
		},
		scales: {
		    yAxes: [{
			scaleLabel: {
			    display: true,
			    labelString: 'number of issues detected'
			},

			ticks: {
			    min: 0,
			    // max: 100,
			    // beginAtZero: true
			}

		    }],
		    xAxes: [{
			scaleLabel: {
			    display: true,
			    labelString: 'nodes'
			}
		    }]
		}
            }
	});
    }


    let create_doug_chart = function(data) {
	//CREATING DOUGHNUT CHART
	let nodes = new Array(37);
	$.each(nodes, function (index/*, value*/) {
	    let node = index + 1;

	    let doughnut = '<div class="n' + node + '"><canvas id="chart-area' + node
		+ '" width="70" height="70"></canvas></div>';
	    $("#doughnut_container").append(doughnut);

	    let ctx = document.getElementById("chart-area"+node).getContext("2d");
	    window.myDoughnut = new Chart(ctx, {
		type: 'doughnut',
		data: {
		    datasets: [{
			data: parse_each_type_issue(data, node),
			backgroundColor: ['rgba(255, 161, 0, 0.7)', 'rgba(31, 54, 177, 0.7)',
					  'rgba(194,111,225,.7)', 'rgba(28, 255, 0, 0.7)'],
			label: 'dataset 1'
		    }],
		    labels: ["start","load","zombie","no issues"]
		},
		options: {
		    responsive: false,
		    legend: {
			display: false,
			position: 'top',
		    },
		    title: {
			display: false,
			text: ''
		    },
		    animation: {
			animateScale: false,
			animateRotate: true
		    },
		    tooltips: {
          		enabled: false,
          	    },
		    showPercentage: true,
		}
	    });
	});
    }


    //refactoring to put percents label in doughnuts
    Chart.pluginService.register({
  	afterDraw: function (chart/*, easing*/) {
  	    if (chart.config.options.showPercentage || chart.config.options.showLabel) {
  		let self = chart.config;
  		let ctx = chart.chart.ctx;

  		ctx.font = '10px Arial';
  		ctx.textAlign = "center";
  		ctx.fillStyle = "#000";

  		self.data.datasets.forEach(function (dataset/*, datasetIndex*/) {
  		    let total = 0, //total values to compute fraction
  			labelxy = [],
  			offset = Math.PI / 2, //start sector from top
  			radius,
  			centerx,
  			centery,
  			lastend = 0; //prev arc's end line: starting with 0

  		    for (let val of dataset.data) { total += val; }

  		    //TODO needs improvement
  		    let i = 0;
  		    let meta = dataset._meta[i];
  		    while(!meta) {
  			i++;
  			meta = dataset._meta[i];
  		    }

  		    let element;
  		    for(let index = 0; index < meta.data.length; index++) {

  			element = meta.data[index];
  			radius = 1.23 * element._view.outerRadius - element._view.innerRadius;
  			centerx = element._model.x;
  			centery = element._model.y;
  			let thispart = dataset.data[index],
  			    arcsector = Math.PI * (2 * thispart / total);
  			if (element.hasValue() && dataset.data[index] > 0) {
  			    labelxy.push(lastend + arcsector / 2 + Math.PI + offset);
  			}
  			else {
  			    labelxy.push(-1);
  			}
  			lastend += arcsector;
  		    }


  		    let lradius = radius;// * 3 / 4;
  		    for (let idx in labelxy) {
  			if (labelxy[idx] === -1) continue;
  			let langle = labelxy[idx],
  			    dx = centerx + lradius * Math.cos(langle),
  			    dy = centery + lradius * Math.sin(langle),
  			    val = Math.round(dataset.data[idx] / total * 100);
  			if (chart.config.options.showPercentage)
  			    ctx.fillText(''+ val + '', dx, dy);
  			else
  			    ctx.fillText(chart.config.data.labels[idx], dx, dy);
  		    }
  		    ctx.restore();
  		});
  	    }
  	}
    });


    let range = function(j, k) {
	return Array
	    .apply(null, Array((k - j) + 1))
	    .map(function(discard, n){ return n + j; });
    }


    let selectInterval = function(data, start, end) {
	let requiredData = _.filter(data, function(data){
	    data.date = moment(new Date(data.date));
	    return data.date > start.startOf('day') && data.date <= end.endOf('day');
	});
	return requiredData;
    }


    let randomColor = function() {
	return 'rgba('
	    + randomColorFactor() + ','
	    + randomColorFactor() + ','
	    + randomColorFactor() + ',.7)';
    };


    let randomColorFactor = function() {
	return Math.round(Math.random() * 255);
    };


    let post_request = function(urlpath, request, callback) {
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", urlpath, true);
	xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	let csrftoken = getCookie('csrftoken');
	xhttp.setRequestHeader("X-CSRFToken", csrftoken);
	xhttp.send(JSON.stringify(request));
	xhttp.onreadystatechange = function(){callback(xhttp);};
    }


    let main = function() {
	// gets the json file from nigthly routine
	let request = {"file" : 'nigthly'};
	post_request('/files/get', request, function(xhttp) {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {
		let answer = JSON.parse(xhttp.responseText);
		if (answer)
		    build_line_and_doug_chart(answer);
		build_heat_chart(answer);
	    }
	});
    }


    main();
});
