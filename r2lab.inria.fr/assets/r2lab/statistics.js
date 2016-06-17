$(document).ready(function() {
  var version = '1.0';
  var now   = moment();



  var build_data_chart = function(data) {
    var start = moment().subtract(7, 'days');
    var end   = moment().subtract(0, 'days');
    var data  = selectInterval(data, start, end);
    var title = '['+start.date()+'-'+end.date()+'] '+now.format('MMM')+' '+now.year();
    var color = randomColor();

    var xax   = range(1,37);
    var val   = new Array(37).fill(0); //ignoring 0 position of the array

    var dataset = {
      label: title,
      hidden: false,
      backgroundColor: color,
      borderColor: color,
      data: [],
    }

    // select data and sum the ocurences of issues at each node
    $.each(data, function (index, value) {
      $.each(value['data'], function (i, v) {
        val[i-1] = val[i-1] + 1;
      });
    });
    dataset.data = val;

    var chartData = {
        labels: xax,
        datasets: []
    };
    chartData.datasets.push(dataset);

    // window.myBar.update();

    create_chart(chartData);
  }



  var create_chart = function(chartData) {
    window.onload = function() {
        var ctx = document.getElementById("canvas").getContext("2d");
        window.myBar = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                // Elements options apply to all of the options unless overridden in a dataset
                // In this case, we are setting the border of each bar to be 2px wide and green
                elements: {
                    rectangle: {
                        borderWidth: 0,

                        borderSkipped: 'bottom'
                    }
                },
                responsive: true,
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    // text: 'last week statistics'
                },
                scales: {
                  yAxes: [{
                    scaleLabel: {
                      display: true,
                      labelString: 'presence of issues detected'
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
    };
  }



  var range = function(j, k) {
    return Array
      .apply(null, Array((k - j) + 1))
      .map(function(discard, n){ return n + j; });
  }



  var selectInterval = function(data, start, end) {
    var requiredData = _.filter(data, function(data){
      data.date = moment(new Date(data.date));
      return data.date >= start && data.date <= end;
    });
    return requiredData;
  }



  var randomColor = function() {
      return 'rgba(' + randomColorFactor() + ',' + randomColorFactor() + ',' + randomColorFactor() + ',.7)';
  };



  var randomScalingFactor = function() {
      return (Math.random() > 0.5 ? 1.0 : 1.0) * Math.round(Math.random() * 100);
  };



  var randomColorFactor = function() {
      return Math.round(Math.random() * 255);
  };



  var main = function() {
    console.log("statistics version " + version);

    // gets the json file from nigthly routine
    var request = {"file" : 'nigthly'};
    post_omfrest_request('/files/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        answer = JSON.parse(xhttp.responseText);
        build_data_chart(answer);
        // $.each(answer, function (index, value) {
          // console.log(value);
        // });
      }
    });
  }



  main();
});
