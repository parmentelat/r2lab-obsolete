$(document).ready(function() {
  var version = '1.0';
  var now = moment();



  var is_last_week = function(week_ago) {
    is_last = false;
    if (week_ago == 1)
      is_last = true;
    return is_last;
  }



  var disable_week = function(week_ago) {
    week_to_disable = [3,4];
    return $.inArray(week_ago, week_to_disable) > -1 ? true : false;
  }



  var build_data_chart = function(data) {
    var w_ago  = [1,2,3,4]; //ex.: 3 means four weeks ago
    var start  = null;
    var end    = null;
    var d_range= [];
    var title  = '';
    var color  = '';
    var xax    = range(0,37); //all nodes
    var val    = null; //ignoring 0 position of the array
    var dataset= {};

    var chartData = {
        labels: xax,
        datasets: []
    };

    $.each(w_ago, function (index, value) {
      start = moment().subtract((value    * 7)-1, 'days');
      end   = moment().subtract((value-1) * 7,    'days');

      d_range  = selectInterval(data, start, end);
      title = is_last_week(value) ? value + ' week' : value + ' weeks';
      color = randomColor();

      dataset = {
        fill: !is_last_week(value),
        borderWidth: 1.7,
        label: title,
        hidden: false,
        backgroundColor: color,
        borderColor: color,
        data: [],
      }

      // select data and sum the ocurences of issues at each node
      val = new Array(38).fill(0);
      $.each(d_range, function (index, value) {
        $.each(value['data'], function (i, v) {
          val[i] = val[i] + 1;
        });
      });
      dataset.data = val;
      chartData.datasets.push(dataset);
    })

    in_cumulative(chartData);

    create_chart (chartData);
  }




  var in_cumulative = function(chartData) {
    //cumulative values to see difference between weeks
    $.each(chartData.datasets, function (index, value) {
      if(index > 0){
        $.each(chartData.datasets[index].data, function (i, v) {
          chartData.datasets[index].data[i] = chartData.datasets[index].data[i] + chartData.datasets[index-1].data[i]
        });
      }
    });
    return chartData;
  }




  var create_chart = function(chartData) {
      //CREATING BAR CHART
      var ctx = document.getElementById("bar").getContext("2d");
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
                  position: 'right',
              },
              title: {
                  display: true,
                  text: 'issues found "n" weeks ago from today'
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
      //CREATING LINE CHART
      ctx = document.getElementById("line").getContext("2d");
      window.myLine = new Chart(ctx, {
          type: 'line',
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
                  position: 'right',
              },
              title: {
                  display: true,
                  text: 'issues found "n" weeks ago from today'
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



  var range = function(j, k) {
    return Array
      .apply(null, Array((k - j) + 1))
      .map(function(discard, n){ return n + j; });
  }



  var selectInterval = function(data, start, end) {
    var requiredData = _.filter(data, function(data){
      data.date = moment(new Date(data.date));
      return data.date > start.startOf('day') && data.date <= end.endOf('day');
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



  var post_request = function(urlpath, request, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", urlpath, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var csrftoken = getCookie('csrftoken');
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send(JSON.stringify(request));
    xhttp.onreadystatechange = function(){callback(xhttp);};
  }



  var main = function() {
    console.log("statistics version " + version);
    // gets the json file from nigthly routine
    var request = {"file" : 'nigthly'};
    post_request('/files/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        answer = JSON.parse(xhttp.responseText);
        if (answer)
          build_data_chart(answer);
      }
    });
  }



  main();
});
