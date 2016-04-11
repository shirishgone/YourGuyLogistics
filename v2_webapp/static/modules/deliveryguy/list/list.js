(function(){
	'use strict';
	/*
		dgListCntrl is the controller for the delivery guy list page. 
		Its resolved after loading all the dgs from the server.
	*/
	var dgListCntrl = function($state,$mdSidenav,$stateParams,dgs,constants,DeliveryGuy,Notification){
		var self = this;
		this.params = $stateParams;
		this.params.start_date = new Date(this.params.start_date);
		this.params.end_date = new Date(this.params.end_date);
		this.dg_status = constants.dg_status;
		this.searchDgActive = (this.params.search !== undefined) ? true : false;
		/*
			@dgs: resolved dgs list accordign to the url prameters.
		*/
		this.dgs = dgs.payload.data.data;
		this.total_pages = dgs.payload.data.total_pages;
		this.total_dgs = dgs.payload.data.total_count;

		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the dg page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('dgList-filter').toggle();
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		this.resetParams = function(){
			self.params = {};
			self.getDgs();
		};
		/*
			@paginate is a function to paginate to the next and previous page of the delivery guy list
		*/
		this.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getDgs();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getDgs();
			}
		};
		/*
			@revertToPageOne is a function to revert back to first page if any kind of filter is applied
		*/ 
		this.revertToPageOne = function(){
			self.params.page = 1;
			self.getDgs();
		};
		/*
			@backFromSearch is a function to revert back from a searched delivery guy name to complete list view of delivery guys
		*/ 
		this.backFromSearch = function(){
			self.params.search = undefined;
			self.searchDgActive = false;
			self.getDgs();
			
		};
		this.downloadAttendance = function(){
			Notification.loaderStart();
			var str = '';
			var noOfdays = Math.ceil(moment.duration(moment(self.params.end_date).diff(moment(self.params.start_date))).asDays());
			var attendance_params = {
				start_date : moment(self.params.start_date).startOf('day').toISOString(),
				end_date   : moment(self.params.end_date).endOf('day').toISOString()
			};
			for(var i = 0 ; i < noOfdays ; i++ ){
				str += ',IsoToDate(attendance ->'+ i +'-> date) AS Date_'+(i+1)+',attendance ->'+ i +'-> worked_hrs AS Hours_'+(i+1);
			}
			DeliveryGuy.dgsAttendance.query(attendance_params,function(response){
				// alasql('SEARCH / AS @a UNION ALL(attendance / AS @b RETURN(@a.name AS Name , IsoToDate(@b.date) AS DATE, @b.worked_hrs AS Hours)) INTO XLSX("attendance.xlsx",{headers:true}) FROM ?',[response.payload.data]);
				var select_str = 'SELECT name AS Name'+str;
				alasql( select_str+' INTO XLSX("attendance.xlsx",{headers:true}) FROM ?',[response.payload.data]);
				Notification.loaderComplete();
			});
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		this.getDgs = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('deliveryguy')
	.controller('dgListCntrl', [
		'$state',
		'$mdSidenav',
		'$stateParams',
		'dgs',
		'constants',
		'DeliveryGuy',
		'Notification',
		dgListCntrl 
	]);
})();