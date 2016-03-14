(function(){
	'use strict';
	var reportsCntrl = function($state,$stateParams,Vendor,report,Notification){
		var self = this;
		self.params = $stateParams;
		self.searchVendor  = self.params.vendor_id;
		self.report_stats = report.payload.data;
		console.log(self.report_stats);

		self.vendorSearchTextChange = function(text){
			console.log(text);
			if(!text){
				console.log("none");
			}
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				return response.payload.data.data;
			});
		};
		self.selectedVendorChange = function(vendor){
			if(vendor){
				self.params.vendor_id = vendor.id;
			}
			else{
				self.params.vendor_id = undefined;
			}
			self.getReports();
		};
		self.manipulateGraph = function(){
			self.graphData = {
				chart : {
					plotGradientColor : " ",
					plotSpacePercent : "60",
					caption: "Order Details",
					xaxisname: "Dates",
					yaxisname: "Orders",
					showalternatehgridcolor: "0",
					placevaluesinside: "1",
					toolTipSepChar : '=',
					showborder: "0",
					showvalues: "0",
					showplotborder: "0",
					showcanvasborder: "0",
					theme: "fint"
				},
				categories : [
					{
						category: []
					}
				],
				dataset : [
					{
						seriesname: "Total Delivered",
						color: "39B54A",
						data:[]
					},
					{
						seriesname: "Total Attempted",
						color: "00CCFF",
						data:[]
					},
					{
						seriesname: "Total Intransit",
						color: "FCC06A",
						data:[]
					},
					{
						seriesname: "Total Queued",
						color: "FE5E64",
						data:[]
					},
					{
						seriesname: "Total Cancelled",
						color: "A6A6A6",
						data:[]
					},
				]
			};
			for(var i =0; i < self.report_stats.orders.length;i++){
				self.graphData.categories[0].category[i] = {};
				self.graphData.categories[0].category[i].label = self.report_stats.orders[i].date.slice(8,10);
				self.graphData.dataset[0].data[i] = {
					value : self.report_stats.orders[i].delivered_count ,
					toolText : "Total Delivered:"+self.report_stats.orders[i].delivered_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[1].data[i] = {
					value : self.report_stats.orders[i].delivery_attempted_count+self.report_stats.orders[i].pickup_attempted_count,
					toolText : "Total Attempted:"+(self.report_stats.orders[i].delivery_attempted_count+self.report_stats.orders[i].pickup_attempted_count)+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[2].data[i] = {
					value    : self.report_stats.orders[i].intransit_count,
					toolText : "Total Intransit:"+self.report_stats.orders[i].intransit_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[3].data[i] = {
					value    : self.report_stats.orders[i].queued_count,
					toolText : "Total Queued:"+self.report_stats.orders[i].queued_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
				self.graphData.dataset[4].data[i] = {
					value    : self.report_stats.orders[i].cancelled_count,
					toolText : "Total Cancelled:"+self.report_stats.orders[i].cancelled_count+"{br} Total Placed:"+self.report_stats.orders[i].total_orders_count+"{br}"+new Date(self.report_stats.orders[i].date).toDateString()
				};
			}
			console.log(self.graphData);
		};

		if(self.report_stats.total_orders !== 0){
			self.manipulateGraph();
		}

		/*
			@getReports rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getReports = function(){
			Notification.loaderStart();
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('reports', [
		'ng-fusioncharts'
	])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.reports', {
			url: "^/reports?start_date&end_date&vendor_id",
			templateUrl  : "/static/modules/reports/reports.html",
			controllerAs : 'reports',
    		controller   : "reportsCntrl",
    		resolve: {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			report: ['Reports','$stateParams', function (Reports,$stateParams){
    						$stateParams.start_date = ($stateParams.start_date !== undefined) ? moment($stateParams.start_date).toISOString() : moment().set('date', 1).toISOString();
    						$stateParams.end_date   = ($stateParams.end_date !== undefined) ? moment($stateParams.end_date).toISOString() : moment().toISOString();
    						return Reports.getReport.stats($stateParams).$promise;
    					}]
    		}
		});
	}])
	.controller('reportsCntrl', [
		'$state',
		'$stateParams',
		'Vendor',
		'report',
		'Notification',
		reportsCntrl 
	]);
})();