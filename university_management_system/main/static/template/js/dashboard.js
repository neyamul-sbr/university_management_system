(function ($) {
  "use strict";
  $(function () {
    var $sales_chart = $("#sales-chart");
    $.ajax({
      url: $sales_chart.data("url"),
      success: function (data) {
        var SalesChartCanvas = $("#sales-chart").get(0).getContext("2d");
        var SalesChart = new Chart(SalesChartCanvas, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: [
              {
                label: "Marks",
                data: data.data,
                backgroundColor: "#98BDFF",
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
})(jQuery);
