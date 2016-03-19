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
				templateUrl        : '/static/modules/cod/dialog/verify-deposit.html',
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposit : dp,
				},
			})
			.then(function(dp) {
				Notification.loaderStart();
				COD.verifyDeposits.update(dp,function(response){
					Notification.showSuccess('Proof Download Successful');
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
				templateUrl        : '/static/modules/cod/dialog/decline-deposit.html',
				parent             : angular.element(document.body),
				clickOutsideToClose: false,
				locals             : {
					       deposit : dp,
				},
			})
			.then(function(data) {
				Notification.loaderStart();
				COD.verifyDeposits.update(dp,function(response){
					Notification.loaderComplete();
					Notification.showSuccess('Proof Download Successful');
					self.getDeposits();
				});
			});
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
			url: "^/cod/deposits?page",
			templateUrl: "/static/modules/cod/deposit/deposit.html",
			controllerAs : 'deposit',
    		controller: "codDepositCntrl",
    		resolve : {
    			access: ["Access","constants", function (Access,constants) { 
					var allowed_user = [constants.userRole.ACCOUNTS];
					return Access.hasAnyRole(allowed_user); 
    			}],
    			deposits : ['COD','$stateParams',function(COD,$stateParams){
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