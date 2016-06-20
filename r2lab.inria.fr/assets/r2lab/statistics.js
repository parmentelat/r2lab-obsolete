$(document).ready(function() {
  var version = '1.0';
  var now   = moment();



  var build_data_chart = function(data) {
    var start = moment().subtract(28, 'days');
    var end   = moment().subtract(21, 'days');

    // ===============================================
    // Temporary - first week
    var data1  = selectInterval(data, start, end);
    // var title = '' + start.format('DD/MMM/YY') + ' ' + end.format('DD/MMM/YY');
    var title = '1 week';
    var color = randomColor();

    var xax   = range(1,37);
    var val   = new Array(37).fill(0); //ignoring 0 position of the array

    var dataset1 = {
      fill: true,
      borderWidth: 1.7,
      label: title,
      hidden: false,
      backgroundColor: color,
      borderColor: color,
      data: [],
    }

    // select data and sum the ocurences of issues at each node
    $.each(data1, function (index, value) {
      $.each(value['data'], function (i, v) {
        val[i-1] = val[i-1] + 1;
      });
    });
    dataset1.data = val;

    // ===============================================
    // Temporary - second week
    start = moment().subtract(21, 'days');
    end   = moment().subtract(14, 'days');
    data2  = selectInterval(data, start, end);
    // title = '' + start.format('DD/MMM/YY') + ' ' + end.format('DD/MMM/YY');
    title = '2 weeks';
    color = randomColor();

    xax   = range(1,37);
    val   = new Array(37).fill(0); //ignoring 0 position of the array

    var dataset2 = {
      fill: true,
      borderWidth: 1.7,
      label: title,
      hidden: false,
      backgroundColor: color,
      borderColor: color,
      data: [],
    }

    // select data and sum the ocurences of issues at each node
    $.each(data2, function (index, value) {
      $.each(value['data'], function (i, v) {
        val[i-1] = val[i-1] + 1;
      });
    });
    dataset2.data = val;

    // ===============================================
    // Temporary - third week
    start = moment().subtract(14, 'days');
    end   = moment().subtract(7, 'days');
    data3  = selectInterval(data, start, end);
    // title = '' + start.format('DD/MMM/YY') + ' ' + end.format('DD/MMM/YY');
    title = '3 weeks';
    color = randomColor();

    xax   = range(1,37);
    val   = new Array(37).fill(0); //ignoring 0 position of the array

    var dataset3 = {
      fill: true,
      borderWidth: 1.7,
      label: title,
      hidden: false,
      backgroundColor: color,
      borderColor: color,
      data: [],
    }

    // select data and sum the ocurences of issues at each node
    $.each(data3, function (index, value) {
      $.each(value['data'], function (i, v) {
        val[i-1] = val[i-1] + 1;
      });
    });
    dataset3.data = val;

    // ===============================================
    // Temporary - fourth week
    start = moment().subtract(7, 'days');
    end   = moment().subtract(0, 'days');
    data4  = selectInterval(data, start, end);
    // title = '' + start.format('DD/MMM/YY') + ' ' + end.format('DD/MMM/YY');
    title = '4 weeks';
    color = randomColor();

    xax   = range(1,37);
    val   = new Array(37).fill(0); //ignoring 0 position of the array

    var dataset4 = {
      fill: false,
      borderWidth: 1.7,
      label: title,
      hidden: false,
      backgroundColor: color,
      borderColor: color,
      data: [],
    }

    // select data and sum the ocurences of issues at each node
    $.each(data4, function (index, value) {
      $.each(value['data'], function (i, v) {
        val[i-1] = val[i-1] + 1;
      });
    });
    dataset4.data = val;



    var chartData = {
        labels: xax,
        datasets: []
    };
    chartData.datasets.push(dataset1);
    chartData.datasets.push(dataset2);
    chartData.datasets.push(dataset3);
    chartData.datasets.push(dataset4);

    create_chart(chartData);
    create_chart (chartData);
  }

  var create_chart = function(chartData) {
    window.onload = function() {

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
      return data.date >= start.startOf('day') && data.date <= end.endOf('day');
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



  function post_request(urlpath, request, callback) {
      var xhttp = new XMLHttpRequest();
      xhttp.open("POST", urlpath, true);
      xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      // this is where we retrieve the CSRF token from the context
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
        build_data_chart(answer);
        // $.each(answer, function (index, value) {
        //   console.log(value);
        // });
      }
    });
  }



  main();
});
