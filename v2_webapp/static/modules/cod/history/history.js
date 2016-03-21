(function(){
	'use strict';
	var codHistoryCntrl = function($state,$stateParams,historyDeposits,Notification,Vendor){
		var self = this;
		self.params = $stateParams;
		self.historyDeposits = historyDeposits.payload.data.all_transactions;
		self.total_pages = historyDeposits.payload.data.total_pages;
		self.total_deposits = historyDeposits.payload.data.total_count;
		this.searchVendor = this.params.vendor_id;
		console.log(historyDeposits);

		if(this.params.start_date){
			this.params.start_date = new Date(this.params.start_date);
		}
		if(this.params.end_date){
			this.params.end_date = new Date(this.params.end_date);
		}
		/*
			@paginate is a function to paginate to the next and previous page 
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
			@dgSearchTextChange is a function for Delivery guy search for filter. When ever the filtered dg change, 
			this function is called.

			@selectedVendorChange is a callback function after vendor guy selection in the filter.
		*/
		self.vendorSearchTextChange = function(text){
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
		};
		/*
			@resetParams funcion to reset the filter.
		*/
		self.resetParams = function(){
			self.params = {};
			self.getDeposits();
		};
		/*
			@getDeposits rleoads the cod controller according too the filter to get the new filtered data.
		*/
		this.getDeposits = function(){
			$state.transitionTo($state.current, self.params, { reload: true, inherit: false, notify: true });
		};
	};

	angular.module('Cod')
	.config(['$stateProvider',function($stateProvider) {
		$stateProvider
		.state('home.cod.history',{
			url: "^/cod/history?page&start_date&end_date&vendor_id",
			templateUrl: "/static/modules/cod/history/history.html",
			controllerAs : 'history',
    		controller: "codHistoryCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			historyDeposits : ['COD','$stateParams',function(COD,$stateParams){
    				$stateParams.start_date = ($stateParams.start_date !== undefined) ? new Date($stateParams.start_date).toISOString() : undefined;
    				$stateParams.end_date = ($stateParams.end_date !== undefined) ? new Date($stateParams.end_date).toISOString() : undefined;
    				$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    				return COD.transactionHistory.get($stateParams).$promise;
    			}],
    		}
		});
	}])
	.controller('codHistoryCntrl', [
		'$state',
		'$stateParams',
		'historyDeposits',
		'Notification',
		'Vendor',
		codHistoryCntrl
	]);
})();