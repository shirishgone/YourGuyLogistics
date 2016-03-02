(function(){
	'use strict';
	var vendorListCntrl = function($state,$mdSidenav,$stateParams,vendors){
		var self = this;
		self.params = $stateParams;
		this.searchVendorActive = (this.params.search !== undefined) ? true : false;
		/*
			@vendors: resolved vendors list accordign to the url prameters.
		*/
		self.vendors = vendors.payload.data.data;
		self.total_pages = vendors.payload.data.total_pages;
		self.total_vendors = vendors.payload.data.total_vendor_count;
		/*
			@paginate is a function to paginate to the next and previous page of the delivery guy list
		*/
		self.paginate = {
			nextpage : function(){
				self.params.page = self.params.page + 1;
				self.getVendors();
			},
			previouspage : function(){
				self.params.page = self.params.page - 1;
				self.getVendors();
			}
		};

		/*
			@backFromSearch is a function to revert back from a searched delivery guy name to complete list view of delivery guys
		*/ 
		self.backFromSearch = function(){
			self.params.search = undefined;
			self.searchVendorActive = false;
			self.getVendors();
			
		};
		/*
			@getOrders rleoads the order controller according too the filter to get the new filtered data.
		*/
		self.getVendors = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('vendor')
	.controller('vendorListCntrl', [
		'$state',
		'$mdSidenav',
		'$stateParams',
		'vendors',
		vendorListCntrl
	]);
})();