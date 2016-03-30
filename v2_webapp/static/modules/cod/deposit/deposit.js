(function(){
	'use strict';
	function VerifyDepositCntrl($mdDialog,deposit){
		var self = this;
		self.deposit = deposit;
		self.cancel = function() {
			$mdDialog.cancel();
		};
		self.answer = function(answer) {
			answer.is_accepted = true;
			$mdDialog.hide(answer);
		};
	}

	function DeclineDepositCntrl($mdDialog,deposit){
		var self = this;
		self.deposit = deposit;
		self.cancel = function() {
			$mdDialog.cancel();
		};
		self.answer = function(answer) {
			answer.pending_salary_deduction = parseFloat(answer.pending_salary_deduction);
			answer.is_accepted = false;
			answer.transaction_id = self.deposit.transaction_id;
			$mdDialog.hide(answer);
		};
	}

	var codDepositCntrl = function($state,$stateParams,$mdDialog,deposits,COD,Notification){
		// variable definations
		var self = this;
		self.params = $stateParams;
		self.deposits = deposits.payload.data.all_transactions;
		self.total_pages = deposits.payload.data.total_pages;
		self.total_deposits = deposits.payload.data.total_bank_deposit_count;
		
		this.searchVendor = this.params.vendor_id;
		if(this.params.start_date){
			this.params.start_date = new Date(this.params.start_date);
		}
		if(this.params.end_date){
			this.params.end_date = new Date(this.params.end_date);
		}
		/*
			@showImage is a function to show the image of the deposit reciept which dg submits as a proof 
			of the cod amount deposited in the bank account.
		*/
		self.showImage = function(url){
			url = url.replace(/:/g,'%3A');
			var image_url = 'https://s3-ap-southeast-1.amazonaws.com/bank-deposit-test/'+url;
			self.showImageSection = true;
			self.depositImage = image_url;
		};
		/*
			@verifyDeposit function to open verify deposit popup and send a verify request to server.
		*/
		self.verifyDeposit = function(dp){
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','deposit',VerifyDepositCntrl]),
				controllerAs       : 'verifyDeposit',
				templateUrl        : '/static/modules/cod/dialog/verify-deposit.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposit : dp,
				},
			})
			.then(function(dp) {
				Notification.loaderStart();
				COD.verifyDeposits.update(dp,function(response){
					Notification.showSuccess('Deposit Verified Successfully');
					Notification.loaderComplete();
					self.getDeposits();
				});
			});
		};
		/*
			@declineDeposit is a function to open decline deposit dialog and send a decline request to server.
		*/
		self.declineDeposit = function(dp){
			$mdDialog.show({
				controller         : ('EditDgCntrl',['$mdDialog','deposit',DeclineDepositCntrl]),
				controllerAs       : 'declineDeposit',
				templateUrl        : '/static/modules/cod/dialog/decline-deposit.html?nd=' + Date.now(),
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposit : dp,
				},
			})
			.then(function(data) {
				Notification.loaderStart();
				COD.verifyDeposits.update(data,function(response){
					Notification.loaderComplete();
					Notification.showSuccess('Deposit Declined Successfully');
					self.getDeposits();
				});
			});
		};
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
			@vendorSearchTextChange is a function for vendor guy search for filter. When ever the filtered vendor change, 
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
		.state('home.cod.deposit',{
			url: "^/cod/deposits?page&start_date&end_date&vendor_id",
			templateUrl: "/static/modules/cod/deposit/deposit.html",
			controllerAs : 'deposit',
    		controller: "codDepositCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			deposits : ['COD','$stateParams',function(COD,$stateParams){
    				$stateParams.start_date = ($stateParams.start_date !== undefined) ? new Date($stateParams.start_date).toISOString() : undefined;
    				$stateParams.end_date = ($stateParams.end_date !== undefined) ? new Date($stateParams.end_date).toISOString() : undefined;
    				$stateParams.page = (!isNaN($stateParams.page))? parseInt($stateParams.page): 1;
    				return COD.getDeposits.get($stateParams).$promise;
    			}],
    		}
		});
	}])
	.controller('codDepositCntrl', [
		'$state',
		'$stateParams',
		'$mdDialog',
		'deposits',
		'COD',
		'Notification',
		codDepositCntrl
	]);
})();