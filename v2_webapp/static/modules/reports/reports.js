(function(){
	'use strict';
	var reportsCntrl = function($state,$stateParams,Reports,Vendor,report,Notification){
		var self = this;
		self.params = $stateParams;
		self.searchVendor  = self.params.vednor_name;
		this.searchVendorActive = (this.params.vendor_id !== undefined) ? true : false;
		self.report_stats = report.payload.data;

		self.params.start_date = new Date(self.params.start_date);
		self.params.end_date   = new Date(self.params.end_date);
		self.maxStartDate = moment().toDate();
		self.minStartDate = moment("2015-01-01").toDate();
		self.maxEndDate = moment(self.params.start_date).add(3 , 'months').toDate();

		/*
			@backFromSearch is a function to revert back from a searched vendor view to default view of reports
		*/ 
		this.backFromSearch = function(){
			self.params.vendor_id = undefined;
			self.params.vednor_name = undefined;
			self.searchVendorActive = false;
			self.getReports();
		};
		
		self.vendorSearchTextChange = function(text){
			var search = {
				search : text
			};
			return Vendor.query(search).$promise.then(function (response){
				if(self.params.vendor_id){
					response.payload.data.data.push({name:'All Vendors'});
				}
				return response.payload.data.data;
			});
		};
		self.selectedVendorChange = function(vendor){
			if(vendor.id){
				self.params.vendor_id = vendor.id;
				self.params.vednor_name = vendor.name;
			}
			else{
				self.params.vendor_id = undefined;
				self.params.vednor_name = undefined;
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
		};

		if(self.report_stats.total_orders !== 0){
			self.manipulateGraph();
		}

		self.date_change = function(){
			if( moment(self.params.end_date).diff(self.params.start_date,'months') > 3 ){
				self.params.end_date = moment(self.params.start_date).add(3, 'months').toDate();
			}
			if( moment(self.params.end_date).diff(self.params.start_date,'days') < 0 ){
				self.params.end_date = self.params.start_date;
			}
			self.getReports();
		};


		self.downloadReportExcel = function(){
			Notification.loaderStart();
			Reports.reportsExcel.get(self.params,function(response){
				alasql('SELECT * INTO XLSX("YG_REPORT.xlsx",{headers:true}) FROM ?',[response.payload.data]);
				Notification.loaderComplete();
			});
		};
		/*
			@getReports rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getReports = function(){
			Notification.loaderStart();
			if (!self.params.vendor_id) {
				self.params.vednor_name = undefined;
			}
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('reports', [
		'ng-fusioncharts'
	])
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.reports', {
			url: "^/reports?start_date&end_date&vendor_id&vednor_name",
			templateUrl  : "/static/modules/reports/reports.html",
			controllerAs : 'reports',
    		controller   : "reportsCntrl",
    		resolve: {
    			access: ["Access","constants", function (Access,constants) { 
    						var allowed_user = [constants.userRole.OPS,constants.userRole.OPS_MANAGER,constants.userRole.SALES,constants.userRole.SALES_MANAGER,constants.userRole.VENDOR];
    						return Access.hasAnyRole(allowed_user); 
    					}],
    			report: ['Reports','$stateParams', function (Reports,$stateParams){
    						// var x = new Date();
    						// x.setHours(0);
    						// x.setMinutes(0);
    						// x.setSeconds(0);
    						// x.setDate(1);
    						var x,y;
	    					if(!$stateParams.start_date){
	    						x =  moment();
								x.startOf('day');
	    					}
	    					else{
	    						$stateParams.start_date = moment(new Date($stateParams.start_date));
	    						$stateParams.start_date.startOf('day');
	    					}
	    					if(!$stateParams.end_date){
	    						y =  moment();
								y.endOf('day');
	    					}
	    					else{
	    						$stateParams.end_date = moment(new Date($stateParams.end_date));
	    						$stateParams.end_date.endOf('day');
	    					}
    						$stateParams.start_date = ($stateParams.start_date !== undefined) ? $stateParams.start_date.toISOString() : x.toISOString();
    						$stateParams.end_date   = ($stateParams.end_date !== undefined) ? $stateParams.end_date.toISOString() : y.toISOString();
    						return Reports.getReport.stats($stateParams).$promise;
    					}]
    		}
		});
	}])
	.controller('reportsCntrl', [
		'$state',
		'$stateParams',
		'Reports',
		'Vendor',
		'report',
		'Notification',
		reportsCntrl 
	]);
})();