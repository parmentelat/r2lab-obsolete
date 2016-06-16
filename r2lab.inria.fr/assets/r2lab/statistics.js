$(document).ready(function() {
  var version = '1.0';



  var week_chart = function(json_data) {

    var weke_rewind = 1;
    var now = moment();
    var startDate = moment().subtract(7, 'days');
    var endDate   = moment().subtract(1, 'days');

    var requiredData = _.filter(json_data, function(data){
      data.date = moment(new Date(data.date));
      return data.date >= startDate && data.date <= endDate;
    });

    console.log(requiredData);

    var randomScalingFactor = function() {
        return (Math.random() > 0.5 ? 1.0 : 1.0) * Math.round(Math.random() * 100);
    };
    var randomColorFactor = function() {
        return Math.round(Math.random() * 255);
    };
    var randomColor = function() {
        return 'rgba(' + randomColorFactor() + ',' + randomColorFactor() + ',' + randomColorFactor() + ',.7)';
    };

    var barChartData = {
        labels: range(1,37),
        datasets: [{
            label: '[10-17] Jun 2016',
            backgroundColor: "rgba(220,220,220,0.5)",
            data: [randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor()]
        // }, {
        //     hidden: true,
        //     label: 'Dataset 2',
        //     backgroundColor: "rgba(151,187,205,0.5)",
        //     data: [randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor()]
        // }, {
        //     label: 'Dataset 3',
        //     backgroundColor: "rgba(151,187,205,0.5)",
        //     data: [randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor(), randomScalingFactor()]
        // }]
      }]
    };

    window.onload = function() {
        var ctx = document.getElementById("canvas").getContext("2d");
        window.myBar = new Chart(ctx, {
            type: 'bar',
            data: barChartData,
            options: {
                // Elements options apply to all of the options unless overridden in a dataset
                // In this case, we are setting the border of each bar to be 2px wide and green
                elements: {
                    rectangle: {
                        borderWidth: 2,
                        borderColor: 'rgb(0, 255, 0)',
                        borderSkipped: 'bottom'
                    }
                },
                responsive: true,
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'semanal statistics'
                },
                scales: {
                  yAxes: [{
                    scaleLabel: {
                      display: true,
                      labelString: '% of issues detected'
                    },

                    ticks: {
                        min: 0,
                        max: 100,
                        beginAtZero: true
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

  function range(j, k) {
    return Array
        .apply(null, Array((k - j) + 1))
        .map(function(discard, n){ return n + j; });
  }


  function main(){
    console.log("statistics version " + version);

    // gets the json file from nigthly routine
    var request = {"file" : 'nigthly'};
    post_omfrest_request('/files/get', request, function(xhttp) {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        answer = JSON.parse(xhttp.responseText);
        // $.each(answer, function (index, value) {
          // console.log(value);
        // });
        week_chart(answer);
      }
    });
  }



  main();
});
