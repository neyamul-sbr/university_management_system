(function ($) {
  "use strict";
  $(function () {
    var $sales_chart = $("#sales-chart");
    $.ajax({
      url: $sales_chart.data("url"),
      success: function (data) {
        var SalesChartCanvas = $("#sales-chart").get(0).getContext("2d");
        var barColors = ["red", "green","blue","orange","brown"];
        var SalesChart = new Chart(SalesChartCanvas, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "Marks",
                data: data.data,
                backgroundColor: barColors,
                // backgroundColor: '#98BDFF'
              },
            ],
          },
          options: {
            cornerRadius: 1,
            responsive: true,
            maintainAspectRatio: true,
            layout: {
              padding: {
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
              },
            },
            scales: {
              yAxes: [
                {
                  display: true,
                  gridLines: {
                    display: true,
                    drawBorder: false,
                    color: "#F2F2F2",
                    // color: '#98BDFF',
                  },
                  ticks: {
                    display: true,
                    min: 0,
                    max: 10,
                    callback: function (value, index, values) {
                      return value;
                    },
                    autoSkip: true,
                    maxTicksLimit: 10,
                    fontColor: "#6C7383",
                  },
                },
              ],
              xAxes: [
                {
                  stacked: false,
                  ticks: {
                    beginAtZero: true,
                    fontColor: "#6C7383",
                  },
                  gridLines: {
                    color: "rgba(0, 0, 0, 0)",
                    display: false,
                  },
                  barPercentage: 1,
                },
              ],
            },
            legend: {
              display: false,
            },
            elements: {
              point: {
                radius: 0,
              },
            },
          },
        });
        document.getElementById("sales-legend").innerHTML =
          SalesChart.generateLegend();
      },
    });
  });

  $(function () {
    var $pie_chart = $("#pieChart");
    var barColors = [
      "rgba(0,0,255,1.0)",
      "rgba(0,0,255,0.8)",
      "rgba(0,0,255,0.6)",
      "rgba(0,0,255,0.4)",
      "rgba(0,0,255,0.2)",
    ];
    $.ajax({
      url: $pie_chart.data("url"),
      success: function (data) {
        var pieChartCanvas = $("#pieChart").get(0).getContext("2d");
        var pieChart = new Chart(pieChartCanvas, {
          type: "doughnut",
          data: {
            labels: data.labels,
            datasets: [{
              backgroundColor: barColors,
              data: data.data,
              hoverOffset: 4
            }]
          },
          options: {
            title: {
              display: true,
              text: "Skill-Set On Subject category"
            }
          }
        });
      
    }
  });
});
})(jQuery);
