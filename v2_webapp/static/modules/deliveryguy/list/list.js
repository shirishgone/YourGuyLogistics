(function(){
	'use strict';
	/*
		dgListCntrl is the controller for the delivery guy lst page. 
		Its resolved after loading all the dgs from the server.
			
	*/
	var dgListCntrl = function($state,$mdSidenav,$stateParams,dgs,constants){
		var self = this;
		this.params = $stateParams;
		this.params.date = new Date(this.params.date);
		this.dg_status = constants.dg_status;
		this.searchDgActive = (this.params.search !== undefined) ? true : false;
		/*
			@dgs: resolved dgs list accordign to the url prameters.
		*/
		this.dgs = dgs.payload.data.data;
		this.total_pages = dgs.payload.data.total_pages;
		this.total_dgs = dgs.payload.data.total_dg_count;

		/*
			 @ toggleFilter : main sidenav toggle function, this function toggle the sidebar of the filets of the dg page page.
		*/
		this.toggleFilter = function(){
			$mdSidenav('dgList-filter').toggle();
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
			@backFromSearch is a function to revert back from a searched delivery guy name to complete list view of delivery guys
		*/ 
		this.backFromSearch = function(){
			self.params.search = undefined;
			self.searchDgActive = false;
			self.getDgs();
			
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
		dgListCntrl 
	]);
})();