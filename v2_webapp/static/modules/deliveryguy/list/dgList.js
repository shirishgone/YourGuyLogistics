(function(){
	'use strict';
	/*
		dgListCntrl is the controller for the delivery guy lst page. 
		Its resolved after loading all the dgs from the server.
			
	*/
	var dgListCntrl = function($state,$mdSidenav,$stateParams,dgs){
		var self = this;
		this.params = $stateParams;
		/*
			@dgs: resolved dgs list accordign to the url prameters.
		*/
		this.dgs = dgs.data;
		this.total_pages = dgs.total_pages;
		this.total_dgs = dgs.total_dg_count;

		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the orders page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('dgList-filter').toggle();
		};
		/*
			@paginate is a function to paginate to the next and previous page of the order list
			@statusSelection is a fucntion to select or unselect the status data in order filter
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
		dgListCntrl 
	]);
})();