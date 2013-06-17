/**
 * @fileoverview
 * Provides methods to render Google Visualization Charts on the Dashboard page.
 * @author jfmontesdeoca11@gmail.com (Jose Montes de Oca)
 */

/** global namespace for Web Monitor project. */
var webmonitor = webmonitor || {};

/** GViz object for visualization methods. */
webmonitor.GViz = webmonitor.GViz || {};

/** Load the Visualization API and the core chart package. */
google.load('visualization', '1.0', {'packages':['corechart']});

/**
 * Callback method that creates and populates a DataTable, instantiates the
 * charts and renders them.
 */
webmonitor.GViz.drawVisualizations = function() {

    var loc = window.location;

    var opts = {sendMethod: 'xhr'};

    // Initialize query variable
    var resource = 'http://' + loc.hostname + '/viz/v1/dailyLatency' +
                    loc.pathname;
    console.log('Query resource at '+resource);
    var dashboardQuery = new google.visualization.Query(resource, opts);

    // Send query request
    dashboardQuery.send(webmonitor.GViz.handleDashboardQueryResponse);
};

/**
 * Handles dashboardQuery query callback, which will draw the chart on the
 * page.
 * @param {object} response object containing the dataTable.
 */
webmonitor.GViz.handleDashboardQueryResponse = function(response) {
    console.log('Entering handleDashboardQueryResponse Function.');
    var data = response.getDataTable();
    var chart = new google.visualization.AreaChart(
                      document.getElementById('gchart_daily_latency'));
    chart.draw(data, {width: '100%', height: '400px'});
};

/** Set a callback to run when the Google Visualization API is loaded. */
google.setOnLoadCallback(webmonitor.GViz.drawVisualizations);
